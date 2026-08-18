# 本地 DeepAnalyze-8B 推理服务

本机使用官方 llama.cpp Vulkan 后端加载 Q4_K_M GGUF 权重，并提供 OpenAI 兼容 API。

当前配置：

- GPU：RTX 4060 Laptop 8GB（Vulkan1）
- 模型：DeepAnalyze-8B Q4_K_M，约 4.68GB
- 上下文：4096 tokens
- 并行请求：1
- 模型地址：`http://127.0.0.1:8000/v1`
- 后端地址：`http://127.0.0.1:8200`
- 网页地址：`http://127.0.0.1:4000`

## 一键运行

从仓库根目录启动全部服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_local.ps1
```

停止全部服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local.ps1
```

也可以分别运行 `start_local_model.ps1`、`start_local_backend.ps1`、`start_local_frontend.ps1` 及对应的停止脚本。

## 健康检查

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8200/health
Invoke-RestMethod http://127.0.0.1:4000/api/health
```

日志位于 `.local-logs`。服务只监听 `127.0.0.1`，不能直接作为公网模型服务使用。权重和 llama.cpp 运行时均放在 Git 仓库之外。

脚本默认从仓库的上一级目录寻找 `models` 和 `runtimes`。如果目录不同，可以设置 `DATAPILOT_MODEL_PATH`、`DATAPILOT_LLAMA_SERVER`、`DATAPILOT_PYTHON` 和 `DATAPILOT_NODE` 环境变量覆盖路径。
