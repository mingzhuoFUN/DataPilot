# 部署与远程 API

## 方案 A：作品集演示（无权重）

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
```

访问 `http://服务器IP:8080`。该模式使用仓库内 mock provider，适合验证 UI、文件工作区、流式协议和报告下载。

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

## 方案 C：未来 GPU 自托管权重

1. 租用带 NVIDIA GPU 和持久化数据盘的云服务器。
2. 把权重下载到数据盘，例如 `/data/models/DeepAnalyze-8B`，不要放进 Git 仓库。
3. 用 vLLM 启动 OpenAI 兼容服务。
4. 将 `DATAPILOT_MODEL_API_BASE` 指向该服务的 `/v1`。

这一步只替换 provider，不改变前端、网关和业务后端。本项目当前不执行权重下载与 GPU 部署。

## 生产检查清单

- 使用 HTTPS 和域名反向代理，只开放网关端口。
- 将 key 存在平台 Secret，设置 `DATAPILOT_ALLOW_CLIENT_PROVIDER_CONFIG=false`。
- 把 CORS 改成实际域名，限制上传大小。
- 为工作区卷配置备份、容量和生命周期。
- 对公开多用户场景，把代码执行迁移到隔离容器/作业队列并增加身份认证、配额和审计。
- 用 `docker compose logs -f` 和 `/api/health` 检查运行状态。

## 当前环境说明

仓库的 Compose 配置已通过静态验证。若本机 Docker Desktop 的 Linux Engine 未启动，镜像构建会失败；启动 Docker Desktop 后重新运行 `docker compose up --build` 即可。公开云端 URL 还需要用户选择并授权具体云平台、域名和计费账户。
