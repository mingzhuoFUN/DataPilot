# 部署与远程 API

## 方案 A：作品集演示（无权重）

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
```

访问 `http://服务器IP:8080`。该模式使用仓库内 mock provider，适合验证 UI、文件工作区、流式协议和报告下载。

### Render 一键部署

仓库根目录的 `render.yaml` 与 `deploy/Dockerfile.all-in-one` 会把 Nginx、Next.js、FastAPI 和 mock provider 打包为一个 Web Service。在 Render 控制台选择 **New → Blueprint** 并连接此 GitHub 仓库即可创建演示服务。首次创建时可将 `DATAPILOT_MODEL_API_KEY` 留空；接入真实 API 时再在平台 Secret 中设置。

单容器模式默认使用临时工作区，适合作品集演示。若需要长期保存用户文件，应选择持久磁盘并挂载到 `/app/workspace`。

## 方案 B：远程 OpenAI 兼容 API

在 `.env` 或托管平台 Secret 中设置：

```dotenv
DATAPILOT_MODEL_PROVIDER=custom
DATAPILOT_MODEL_API_BASE=https://provider.example/v1
DATAPILOT_MODEL_NAME=model-id
DATAPILOT_MODEL_API_KEY=replace-me
DATAPILOT_ALLOW_CLIENT_PROVIDER_CONFIG=false
DATAPILOT_CORS_ORIGINS=https://demo.example.com
```

重新创建服务：

```bash
docker compose up --build -d
```

`DATAPILOT_ALLOW_CLIENT_PROVIDER_CONFIG=false` 可阻止访客通过浏览器覆盖服务器模型地址与密钥。不要把真实 `.env` 提交到 GitHub。

## 方案 C：Windows 本地 GPU 权重（已验证）

当前开发机已经使用 RTX 4060 Laptop 8GB、llama.cpp Vulkan 和 DeepAnalyze-8B Q4_K_M GGUF 跑通真实推理。权重与运行时位于 Git 仓库外。配置完成后，在仓库根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_local.ps1
```

打开 <http://127.0.0.1:4000>。模型、后端和前端分别监听本机 `8000`、`8200`、`4000` 端口。停止时执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local.ps1
```

详细配置见 `local_inference/README_ZH.md`。

## 方案 D：未来 GPU 云端自托管权重

1. 租用带 NVIDIA GPU 和持久化数据盘的云服务器。
2. 把权重下载到数据盘，例如 `/data/models/DeepAnalyze-8B`，不要放进 Git 仓库。
3. 用 vLLM 启动 OpenAI 兼容服务。
4. 将 `DATAPILOT_MODEL_API_BASE` 指向该服务的 `/v1`。

这一步只替换 provider，不改变前端、网关和业务后端。本地权重部署已经完成，云端迁移留到公网演示的最后阶段。

## 生产检查清单

- 使用 HTTPS 和域名反向代理，只开放网关端口。
- 将 key 存在平台 Secret，设置 `DATAPILOT_ALLOW_CLIENT_PROVIDER_CONFIG=false`。
- 把 CORS 改成实际域名，限制上传大小。
- 为工作区卷配置备份、容量和生命周期。
- 对公开多用户场景，把代码执行迁移到隔离容器/作业队列并增加身份认证、配额和审计。
- 用 `docker compose logs -f` 和 `/api/health` 检查运行状态。

## 当前环境说明

仓库的 Compose 配置已通过静态验证，GitHub Actions 还会实际构建并启动单容器部署镜像进行健康检查。若本机 Docker Desktop 的 Linux Engine 未启动，镜像构建会失败；启动 Docker Desktop 后重新运行 `docker compose up --build` 即可。公开云端 URL 还需要用户在 Render 等平台授权 GitHub 仓库并确认服务创建。
