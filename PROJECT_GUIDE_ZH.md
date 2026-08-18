# DataPilot 项目总览

> 更新日期：2026-08-18  
> 仓库：<https://github.com/mingzhuoFUN/DataPilot>  
> 当前开发分支：`agent/local-deepanalyze-runtime`

## 1. 项目介绍

DataPilot 是一个可在浏览器中使用的自主数据分析工作台。用户可以上传 CSV、Excel、SQLite、JSON、文本或图片等数据文件，以自然语言描述分析任务，由模型完成分析规划、Python 代码生成、代码执行、结果理解和报告输出。

本项目以开源项目 [ruc-datalab/DeepAnalyze](https://github.com/ruc-datalab/DeepAnalyze) 为基础，保留其模型动作协议、训练与评测资源，并在此基础上完成以下工程化工作：

- 将研究项目包装成可运行的 Next.js + FastAPI Web 应用；
- 接入本地 DeepAnalyze-8B、远程 OpenAI 兼容 API 和 Mock 模型；
- 在 RTX 4060 8GB 显存环境下完成 Q4_K_M 本地量化部署；
- 增加文件工作区、代码执行、文件预览、报告导出和分类下载；
- 增加 Docker、CI、测试、安全限制和一键启动脚本；
- 将前端重构为独立的 DataPilot 品牌视觉，而不是直接沿用上游页面。

本项目不声称自行训练了 DeepAnalyze-8B。模型、论文及上游研究成果归原作者所有，本项目的主要个人工作是 Web 化、API 适配、本地量化部署、工程化、测试和产品视觉重构。

## 2. 当前完成度

当前本地可运行版本约完成 **90%–95%**。

### 已完成

- DeepAnalyze-8B 官方原始权重已下载，约 15.27GB；
- 原始权重已转换为约 4.68GB 的 Q4_K_M GGUF；
- 使用 llama.cpp Vulkan 在 RTX 4060 Laptop 8GB 上成功推理；
- 本地模型提供 OpenAI 兼容 API：`http://127.0.0.1:8000/v1`；
- FastAPI 后端已接入本地模型：`http://127.0.0.1:8200`；
- Next.js 网页已接入后端：`http://127.0.0.1:4000`；
- `<Analyze>`、`<Code>`、`<Execute>`、`<Understand>`、`<Answer>`、`<File>` 动作协议能够被解析和展示；
- 已完成真实 CSV 上传、Python 执行、聚合分析、结果 CSV 和 Markdown 报告生成；
- 严格验收案例正确得到 Notebook 汇总收入 `25,800`；
- 后端 Pytest、Python 编译、TypeScript 和 Next.js 生产构建均通过；
- 已增加一键启动、停止和端到端测试脚本；
- 前端已重构为 DataPilot 独立视觉风格。

### 尚未完成

- 本地最新分支尚未成功推送 GitHub：当前 GitHub CLI 登录令牌失效，且最近出现 GitHub DNS/网络连接失败；
- 尚无稳定的公网演示地址；
- 公网版本尚未增加用户认证、限流、多用户工作区隔离和生产级代码沙箱；
- Q4_K_M 适合本地部署展示，但分析质量弱于 BF16 原始权重和更强的云端模型；
- 还可以补充新版页面截图、演示 GIF/视频及更完整的作品集材料。

## 3. 系统架构

```text
浏览器
  │
  ▼
Next.js 前端 :4000
  │ /api 反向代理
  ▼
FastAPI 业务后端 :8200
  ├─ 文件上传与工作区管理
  ├─ 动作协议解析
  ├─ Python 代码执行
  ├─ 文件预览与下载
  └─ Markdown / PDF 报告导出
  │ OpenAI 兼容协议
  ▼
llama.cpp 模型服务 :8000
  │
  ▼
DeepAnalyze-8B Q4_K_M / RTX 4060 8GB
```

模型层也可以替换为远程 OpenAI 兼容 API，前端和业务后端不需要重写。

## 4. 前端页面内容

当前前端名称为 **DataPilot · Local Analysis Lab**，使用青绿色主色和橙色强调色，已经与上游 DeepAnalyze 的黑白页面明显区分。

页面由三个主要区域组成：

1. **Workspace（左栏）**
   - 中英文切换；
   - 分析 Prompt 预设；
   - System Prompt；
   - 模型来源、模型名称和温度；
   - 文件上传、文件筛选和分类打包下载。

2. **Analysis Flight Log（中栏）**
   - 用户对话；
   - 流式分析过程；
   - Python 代码与执行输出；
   - 最终答案及生成文件；
   - 代码工作台和报告导出。

3. **Result Observatory（右栏）**
   - 当前文件预览；
   - 上传文件和生成文件统计；
   - CSV/Excel/SQLite/文本/图片等格式预览；
   - 结果下载和工作区管理。

顶部使用独立 `DP` 标识，并展示：

```text
DATA → REASON → EXECUTE → DELIVER
```

## 5. 模型文件与运行环境

模型和运行时均放在 Git 仓库之外，避免误上传 GitHub。

| 内容 | 本机位置 | 说明 |
|---|---|---|
| 原始 DeepAnalyze-8B 权重 | `E:\data agent\models\DeepAnalyze-8B` | 约 15.27GB，BF16 原始文件 |
| BF16 GGUF 中间文件 | `E:\data agent\models\DeepAnalyze-8B-GGUF\DeepAnalyze-8B-BF16.gguf` | 转换产物，体积较大 |
| 当前 Q4 模型 | `E:\data agent\models\DeepAnalyze-8B-GGUF\DeepAnalyze-8B-Q4_K_M.gguf` | 约 4.68GB，本地实际运行版本 |
| llama.cpp Vulkan | `E:\data agent\runtimes\llama-vulkan` | 本地模型服务运行时 |
| Python 环境 | `E:\data agent\runtimes\deepanalyze` | 后端、测试与数据分析依赖 |
| 用户工作区 | `E:\data agent\workspaces` | 上传文件、代码产物和报告 |

Q4_K_M 仍然是 DeepAnalyze-8B 的约 80 亿参数模型，只是参数精度由 BF16 压缩到约 4 bit；它不是新的小参数模型，但会有一定质量损失。

## 6. 仓库目录与文件说明

### 根目录

| 文件或目录 | 内容 |
|---|---|
| `README.md` | 项目首页、快速启动、远程 API、本地开发与验证说明 |
| `PROJECT_PROGRESS_ZH.md` | 按阶段记录的项目进度和后续目标 |
| `PROJECT_GUIDE_ZH.md` | 当前这份项目介绍、进度和文件总览 |
| `REPRODUCTION_ZH.md` | 基于上游项目复现和包装的说明 |
| `UPSTREAM.md` | 上游来源、归属和个人工作边界 |
| `SECURITY.md` | 密钥、上传、代码执行和公网部署安全说明 |
| `LICENSE` | 仓库许可证 |
| `.env.example` | 环境变量模板，不包含真实密钥 |
| `.gitignore` | 忽略日志、环境、模型和临时文件 |
| `compose.yaml` | Docker Compose 编排配置 |
| `render.yaml` | Render Blueprint 部署配置 |
| `requirements.txt` | 根项目 Python 依赖 |
| `pytest.ini` | Pytest 配置 |
| `run.py`、`deepanalyze.py`、`quantize.py` | 上游模型运行与量化入口 |

### `demo/chat_v2/`：当前主要 Web 应用

| 文件或目录 | 内容 |
|---|---|
| `backend.py` | FastAPI 后端启动入口 |
| `backend_app/app.py` | 创建并配置 FastAPI 应用 |
| `backend_app/settings.py` | 模型、工作区、上传、安全和执行设置 |
| `backend_app/routers/chat.py` | 对话、流式响应、停止请求和代码执行接口 |
| `backend_app/routers/workspace.py` | 上传、预览、下载、移动和删除文件接口 |
| `backend_app/routers/export.py` | Markdown/PDF 报告导出接口 |
| `backend_app/services/chat.py` | 模型请求、动作标签解析、多轮执行和报告保存 |
| `backend_app/services/execution.py` | Python 代码安全执行与产物登记 |
| `backend_app/services/docker_executor.py` | Docker 隔离执行后端 |
| `backend_app/services/workspace.py` | 会话工作区、文件树、预览和下载逻辑 |
| `backend_app/services/exporter.py` | 报告整理、Markdown 和 PDF 导出 |
| `requirements.txt` | Web 后端 Python 依赖 |
| `Dockerfile.backend` | 后端容器镜像 |
| `Dockerfile.exec` | 代码执行容器镜像 |

### `demo/chat_v2/frontend/`：DataPilot 前端

| 文件或目录 | 内容 |
|---|---|
| `app/page.tsx` | 首页入口 |
| `app/layout.tsx` | 页面元数据、字体、主题和全局布局 |
| `app/globals.css` | DataPilot 品牌颜色、顶部标识、路线条和全局样式 |
| `components/three-panel-interface.tsx` | 三栏工作台的核心功能与交互 |
| `components/ui/` | Button、Card、Dialog、Tabs、Table 等通用 UI 组件 |
| `lib/config.ts` | 前端 API 地址和端点配置 |
| `lib/prompt-presets.ts` | 中英文分析 Prompt 预设 |
| `lib/monaco-config.ts` | Monaco 代码编辑器配置 |
| `next.config.mjs` | Next.js 构建、图片和后端代理配置 |
| `package.json` | 前端依赖和 build/dev/start 命令 |
| `Dockerfile` | 前端容器镜像 |

### `scripts/`：本地运行与验证

| 文件 | 内容 |
|---|---|
| `start_local.ps1` | 按顺序启动模型、后端和前端 |
| `stop_local.ps1` | 停止整套本地服务 |
| `start_local_model.ps1` | 启动 llama.cpp DeepAnalyze 模型服务 |
| `stop_local_model.ps1` | 安全停止模型进程 |
| `start_local_backend.ps1` | 配置本地 provider 并启动 FastAPI |
| `stop_local_backend.ps1` | 安全停止后端进程 |
| `start_local_frontend.ps1` | 启动 Next.js 生产页面 |
| `stop_local_frontend.ps1` | 停止前端进程 |
| `test_local_stack.ps1` | 检查三项服务并运行最小真实模型请求 |
| `test_local_csv_e2e.py` | 通过网页代理完成真实 CSV 分析和报告验收 |

### 其他重要目录

| 目录 | 内容 |
|---|---|
| `deepanalyze/` | 上游训练、评测、推理与研究代码，保留用于学习和归属 |
| `API/` | 上游/兼容 API 服务代码与示例 |
| `demo/mock_vllm/` | 无需模型和 API Key 的 Mock OpenAI 兼容服务 |
| `demo/chat/` | 上游旧版 Web Demo；当前主要使用 `chat_v2` |
| `demo/cli/` | 命令行调用示例 |
| `demo/jupyter/` | Jupyter 分析服务和工具示例 |
| `deploy/` | Nginx、单容器入口和一体化部署文件 |
| `docker/` | 上游 Docker 配置 |
| `docs/` | 架构、部署、FAQ、简历和 API 使用文档 |
| `tests/` | 后端安全与接口测试 |
| `.github/workflows/` | GitHub Actions CI |
| `.local-logs/` | 本地服务和测试日志，不提交 Git |

## 7. 本地运行方法

### 启动完整项目

```powershell
cd "E:\data agent\DataPilot"
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\start_local.ps1
```

看到以下内容表示启动完成：

```text
DataPilot is ready: http://127.0.0.1:4000
```

打开：<http://127.0.0.1:4000>

完整启动会占用约 5GB 显存。只查看界面时可以仅启动：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_local_frontend.ps1
```

### 停止项目

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local.ps1
```

### 健康检查

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8200/health
Invoke-RestMethod http://127.0.0.1:4000/api/health
```

### 测试

```powershell
python -m pytest -q
powershell -ExecutionPolicy Bypass -File .\scripts\test_local_stack.ps1
python .\scripts\test_local_csv_e2e.py
```

## 8. 已验证结果

| 验证项目 | 结果 |
|---|---|
| RTX 4060 识别与 Vulkan 推理 | 通过 |
| DeepAnalyze-8B Q4 模型加载 | 通过 |
| OpenAI 兼容 `/v1/chat/completions` | 通过 |
| 特殊动作标签保留 | 通过 |
| FastAPI 后端真实模型请求 | 通过 |
| Next.js `/api` 代理 | 通过 |
| CSV 上传与工作区读取 | 通过 |
| Python 代码执行 | 通过 |
| 汇总结果 CSV 生成 | 通过 |
| Markdown 报告生成 | 通过 |
| Pytest 后端测试 | 4 项通过 |
| Next.js 生产构建与 TypeScript | 通过 |
| 一键启动和停止 | 通过 |

## 9. Git 状态与 GitHub 同步

当前本地分支：

```text
agent/local-deepanalyze-runtime
```

主要本地提交：

```text
74d3373 Add local DeepAnalyze runtime
f43b479 Redesign DataPilot analysis workspace
```

远程 `main` 目前尚未包含这两个提交。同步前需要恢复 GitHub 网络，并重新执行：

```powershell
gh auth refresh -h github.com
```

授权完成后推送分支、创建 Pull Request，并合并到 `main`。

## 10. 后续路线

1. 完成 GitHub 重新授权和远程同步；
2. 为 README 增加新版页面截图和真实演示结果；
3. 决定公开演示使用远程高质量 API，还是云端 BF16 DeepAnalyze；
4. 增加登录、限流、HTTPS、多用户隔离和生产级代码沙箱；
5. 部署可公开访问的网页；
6. 整理简历描述、项目演示 GIF 和面试讲解材料。

## 11. 安全与归属

- 模型权重、运行时、`.env`、API Key 和日志不得提交 GitHub；
- 公网环境不能直接暴露无认证的模型 `8000` 端口；
- 本地 `execution_mode=local` 只适合个人可信环境；
- 公网代码执行必须使用容器隔离、资源限制、超时和用户工作区隔离；
- 对外介绍必须明确 DeepAnalyze 上游来源，不应声称自行训练其模型。

