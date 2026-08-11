# DataPilot 项目进度与目标

更新日期：2026-08-11

## 项目定位

DataPilot 基于开源项目 [ruc-datalab/DeepAnalyze](https://github.com/ruc-datalab/DeepAnalyze) 构建。仓库保留上游的模型协议、训练/评测资源和 WebUI 设计基准，并补充可运行的 Web 应用、后端适配、部署脚本、测试与文档。项目不声称自行训练了 DeepAnalyze-8B，归属说明见 `UPSTREAM.md`。

## 当前已经完成

- 独立公开仓库：<https://github.com/mingzhuoFUN/DataPilot>。
- Next.js 三栏式数据分析工作台与 FastAPI 业务后端。
- 文件上传、工作区管理、流式动作协议、Python 执行和 Markdown 报告生成。
- Mock、远程 OpenAI 兼容 API、本地 DeepAnalyze 三种模型接入方式。
- Docker Compose、单容器部署、Render 配置、测试和 GitHub Actions CI。
- DeepAnalyze-8B 官方原始权重已下载到 `E:\data agent\models\DeepAnalyze-8B`（约 15.27GB，不进入 Git）。
- 已将原始权重转换并量化为 Q4_K_M GGUF：`E:\data agent\models\DeepAnalyze-8B-GGUF\DeepAnalyze-8B-Q4_K_M.gguf`（约 4.68GB）。
- 已使用官方 llama.cpp Vulkan 后端在 RTX 4060 Laptop 8GB 上成功加载模型；上下文 4096，单请求运行，显存占用约 5.1GB。
- 本地 OpenAI 兼容模型 API 已运行在 `127.0.0.1:8000`，最小真实推理约 47 tokens/s，并保留 `<Analyze>`、`<Code>`、`<Execute>`、`<Answer>` 协议标签。
- DataPilot 后端已接入本地 API，运行在 `127.0.0.1:8200`；真实端到端请求已生成完整分析、答案和 Markdown 报告。
- Next.js 生产构建通过，网页运行在 `127.0.0.1:4000`；首页与 `/api/health` 代理均返回 200。
- 已提供模型、后端、前端的独立启动/停止脚本以及整套一键脚本。

## 当前本地启动方法

在仓库根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_local.ps1
```

模型首次启动通常需要几十秒。完成后打开 <http://127.0.0.1:4000>。

停止全部服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local.ps1
```

日志统一保存在 `.local-logs`。模型权重与运行时位于仓库外，不会上传 GitHub。

## 已验证链路

```text
浏览器 :4000
  -> Next.js /api 代理
  -> FastAPI :8200
  -> llama.cpp OpenAI 兼容 API :8000
  -> DeepAnalyze-8B Q4_K_M（RTX 4060）
  -> 动作协议解析 / Python 执行 / 报告保存
```

## 接下来要完成

- 使用真实 CSV/Excel 在页面上完成一次人工端到端验收并保存演示截图。
- 补充自动健康检查与更友好的启动失败提示。
- 重新运行完整 pytest、前端构建和仓库安全检查。
- 整理 README 中的本地权重部署说明与简历项目描述。
- 提交并推送本轮本地部署代码到 GitHub。
- 最后阶段再建设公网演示：公开网页不能直接暴露无认证的本地模型端口，需要认证、限流、HTTPS 和稳定的模型在线方案。

## 尚未实现

- 当前网页仅可由本机访问，还没有正式公网演示地址。
- 本地电脑关机或模型服务停止后，真实模型能力不可用。
- 尚未完成多用户隔离、认证、限流、审计和生产级代码执行沙箱。
- 8GB 显存版本为 Q4 量化，效果会接近但不等同于原始 BF16 权重。

## 安全与归属约束

- API Key 只放在本地 `.env` 或托管平台 Secret，不得提交 GitHub。
- 原始权重、GGUF 权重及推理运行时均保存在 Git 仓库外。
- 公网部署时只开放 Web 网关，不直接暴露无认证的 `8000` 模型端口。
- README 和简历必须明确：模型与上游研究成果归 DeepAnalyze 原作者；本项目工作重点是 Web 化、API 适配、本地量化部署、工程化与测试。
