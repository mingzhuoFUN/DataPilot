# DataPilot

DataPilot is a web-based autonomous data analysis agent built on the open-source
DeepAnalyze project. It lets users upload data files, ask analytical questions,
stream model reasoning and Python execution, preview generated charts, and export
analysis reports from a browser.

> Status: initial public baseline. The upstream application is preserved while
> the independent branding, provider configuration, deployment workflow, and
> portfolio documentation are developed incrementally.

## What is included

- Next.js WebUI v2
- FastAPI backend and file service
- CSV, Excel, database, text, and document workspaces
- Streaming `<Analyze>`, `<Code>`, `<Execute>`, and `<Answer>` sections
- Local or Docker-based Python execution
- Generated chart and file previews
- Markdown and PDF report export
- Local, HeyWhale, and custom OpenAI-compatible model providers
- Mock vLLM service for development without model weights
- Training and evaluation resources retained from the upstream repository

## Quick start without model weights

The repository contains a mock vLLM service, so the application pipeline can be
tested before connecting a real model.

Requirements:

- Python 3.12
- Node.js compatible with the bundled Next.js version

Start the mock model:

```powershell
python demo\mock_vllm\start_mock_vllmserver.py
```

Install and start WebUI v2:

```powershell
cd demo\chat_v2\frontend
npm install
cd ..
Copy-Item .env.example .env
start.bat
```

Then open `http://localhost:4000`.

On Windows, set these variables before starting if the console or local proxy
causes startup errors:

```powershell
$env:PYTHONUTF8 = "1"
$env:NO_PROXY = "localhost,127.0.0.1"
```

## Model providers

DataPilot can use:

1. the bundled mock service for interface development;
2. a custom OpenAI-compatible remote API;
3. the DeepAnalyze API;
4. a self-hosted DeepAnalyze-8B vLLM endpoint.

Model weights are intentionally excluded from Git. They will later be deployed
on persistent storage attached to a GPU server.

## Project roadmap

- [x] Preserve a runnable upstream baseline
- [x] Verify the mock model, file upload, API, and code execution pipeline
- [ ] Complete independent visual branding
- [ ] Validate WebUI v2 with a custom remote model API
- [ ] Add production Docker Compose deployment
- [ ] Add CI and automated smoke tests
- [ ] Publish an online demonstration
- [ ] Add optional self-hosted DeepAnalyze-8B deployment

## Upstream and license

DataPilot is derived from
[ruc-datalab/DeepAnalyze](https://github.com/ruc-datalab/DeepAnalyze). The original
project and model were created by the DeepAnalyze authors at Renmin University of
China and Tsinghua University.

This repository retains the upstream MIT license and copyright notice. The
DeepAnalyze-8B model was not trained by the DataPilot maintainer. See
[UPSTREAM.md](UPSTREAM.md) and [LICENSE](LICENSE) for details.

The original upstream README is preserved at
[docs/UPSTREAM_README.md](docs/UPSTREAM_README.md).
