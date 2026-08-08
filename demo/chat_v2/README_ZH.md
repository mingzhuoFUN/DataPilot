# DataPilot Web 应用

[English](README.md) · [项目主页](../../README.md)

此目录包含 DataPilot 的 FastAPI 后端与 Next.js 前端，代码基于 DeepAnalyze WebUI v2 整理和扩展。

## 本地开发

在仓库根目录启动无权重模拟服务：

```powershell
python demo\mock_vllm\start_mock_vllmserver.py
```

启动后端：

```powershell
cd demo\chat_v2
Copy-Item .env.example .env
pip install -r requirements.txt
python backend.py
```

另开终端启动前端：

```powershell
cd demo\chat_v2\frontend
npm ci
npm run dev
```

访问 `http://localhost:4000`，后端地址为 `http://localhost:8200`。

Docker Compose、远程 API、生产注意事项与模型权重路线见[部署文档](../../docs/DEPLOYMENT.md)。

## 模型来源

- `local`：仓库 mock，或本地/自托管 OpenAI 兼容服务。
- `custom`：任意兼容 chat completions 的远程 API。
- `heywhale`：上游保留的 HeyWhale 集成。

公开部署建议设置 `DATAPILOT_ALLOW_CLIENT_PROVIDER_CONFIG=false`，由服务端统一控制模型地址和密钥。
