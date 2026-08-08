# DeepAnalyze 本地复现与源码学习笔记

本文记录在 Windows、Python 3.12 和 8GB NVIDIA GPU 环境下，对 DeepAnalyze
进行的轻量端到端复现。轻量复现使用仓库自带的 mock vLLM 服务，不需要下载
8B 模型，也不会执行训练。

## 1. 当前复现范围

已经验证：

- Python 源码可以通过语法编译检查；
- mock vLLM 服务可以在 `8000` 端口运行；
- OpenAI 兼容 API 可以在 `8200` 端口运行；
- 文件服务可以在 `8100` 端口运行；
- `/health`、`/v1/models`、`/v1/files` 和
  `/v1/chat/completions` 可以串联工作；
- 上传的文件会被复制到按 `thread_id` 隔离的工作区；
- `DeepAnalyzeVLLM.execute_code()` 可以执行 Python，并把标准输出或异常
  转换为下一轮模型可读的 `<Execute>` 反馈。

尚未验证：

- DeepAnalyze-8B 的真实 vLLM 推理；
- WebUI / WebUI v2；
- SFT、冷启动训练和 RL 训练；
- playground 中各数据科学基准的完整评测。

## 2. 环境结论

本次机器环境：

- Windows / PowerShell；
- Python 3.12；
- RTX 4060 Laptop，8GB 显存；
- 没有 Conda 和 Node.js；
- 剩余磁盘空间约 10GB。

官方显存表从 16GB 起，因此当前机器不适合直接部署原始 DeepAnalyze-8B。
即使采用 4-bit 量化，模型文件、运行时和 KV cache 也会让 8GB 显存与当前
磁盘空间非常紧张。建议先使用 mock 或远程 OpenAI-compatible endpoint
学习系统，再在 16GB 以上显存、充足磁盘和 Linux/WSL2 环境中做真实模型复现。

## 3. 创建轻量环境

在仓库根目录执行：

```powershell
python -m venv --system-site-packages .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install `
  openai openpyxl plotly statsmodels websockets pypandoc
```

这里没有安装 `torch`、`transformers` 和 `vllm`，因为 mock/API 复现不需要
加载模型权重。真实推理时应另建独立环境，并按官方 `requirements.txt` 安装。

语法检查：

```powershell
.\.venv\Scripts\python.exe -m compileall -q `
  deepanalyze.py API demo/mock_vllm
```

## 4. Windows 启动注意事项

启动前设置：

```powershell
$env:PYTHONUTF8 = "1"
$env:NO_PROXY = "localhost,127.0.0.1"
```

原因：

1. 两个服务入口会打印 emoji；在 GBK 控制台下可能触发
   `UnicodeEncodeError`，`PYTHONUTF8=1` 可解决。
2. `openai/httpx` 可能读取 Windows 系统代理，并错误地把访问
   `localhost:8000` 的请求发送给代理，表现为空响应的 HTTP 503。
   `NO_PROXY` 可强制本地直连。

终端一，启动 mock 模型：

```powershell
.\.venv\Scripts\python.exe demo\mock_vllm\start_mock_vllmserver.py
```

终端二，启动 API：

```powershell
cd API
..\.venv\Scripts\python.exe start_server.py
```

## 5. 最小端到端验证

健康检查与模型列表：

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8200/health
curl.exe http://localhost:8200/v1/models
```

上传示例 CSV：

```powershell
curl.exe -X POST "http://localhost:8200/v1/files" `
  -F "file=@API/example/Simpson.csv" `
  -F "purpose=file-extract"
```

记录响应中的 `file_id`，然后调用聊天接口：

```powershell
$fileId = "把上传响应中的 file_id 放在这里"
$body = @{
  model = "DeepAnalyze-8B"
  messages = @(
    @{
      role = "user"
      content = "Analyze the uploaded CSV and summarize it."
      file_ids = @($fileId)
    }
  )
  stream = $false
} | ConvertTo-Json -Depth 8

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8200/v1/chat/completions" `
  -ContentType "application/json; charset=utf-8" `
  -Body ([Text.Encoding]::UTF8.GetBytes($body))
```

成功响应中应包含：

- `choices[0].message.content`；
- `choices[0].message.thread_id`；
- mock 返回的文件信息。

## 6. 系统核心机制

DeepAnalyze 的关键不是传统的固定工作流，而是一个由模型驱动的执行循环：

```text
用户问题与数据文件
        |
        v
构造模型消息与工作区信息
        |
        v
模型生成 <Analyze> / <Code> / <Answer>
        |
        +-- 出现 <Code> --> 在工作区执行 Python
        |                    |
        |                    v
        |               生成 <Execute> 反馈和文件清单
        |                    |
        |                    +------ 回到模型继续推理
        |
        +-- 出现 <Answer> --> 输出答案与报告
```

需要重点理解的文件：

1. `deepanalyze.py`
   - 最小、最清晰的 Agent 循环；
   - `generate()` 负责模型调用、标签解析和多轮消息；
   - `execute_code()` 负责执行代码并捕获输出/异常。
2. `API/chat_api.py`
   - 产品化版本的循环；
   - 支持流式输出、线程、上传文件、产物跟踪和报告生成。
3. `API/utils.py`
   - 消息构造、代码执行、文件变化检测和报告生成等基础设施。
4. `API/storage.py`
   - 文件与 thread 工作区的生命周期。
5. `demo/chat_v2/backend_app/`
   - WebUI v2 的后端拆分与本地/Docker 执行模式。
6. `scripts/`
   - 单能力 SFT、多能力冷启动和 RL 三阶段训练入口。
7. `deepanalyze/ms-swift/` 与 `deepanalyze/SkyRL/`
   - 训练框架实现。
8. `playground/`
   - DS-1000、DSBench、TableQA、DABStep 等评测适配。

## 7. 推荐学习顺序

第一阶段：只看 `deepanalyze.py`，手工构造 `<Code>` 和 `<Execute>`，理解
“模型决定下一步、环境提供执行反馈”的闭环。

第二阶段：阅读 `API/chat_api.py`、`API/utils.py` 和 `API/storage.py`，理解
同一闭环如何扩展为多用户 API、文件工作区、流式输出和产物管理。

第三阶段：启动 WebUI v2，追踪一次请求从 Next.js 前端到 FastAPI，再到模型
端点与执行沙箱的完整调用链。

第四阶段：阅读 `scripts/single.sh`、`scripts/multi_coldstart.sh` 和
`scripts/multi_rl.sh`，把论文中的 curriculum-based agentic training
对应到实际训练参数与数据。

第五阶段：从 `playground` 选一个小基准，先用 mock/小模型跑通评测协议，再
替换为真实 DeepAnalyze-8B。

