# DataPilot Web Application

[中文说明](README_ZH.md) · [Project home](../../README.md)

This directory contains the DataPilot FastAPI backend and Next.js frontend, derived from the upstream DeepAnalyze WebUI v2.

## Development

Start the weight-free provider from the repository root:

```bash
python demo/mock_vllm/start_mock_vllmserver.py
```

Start the backend:

```bash
cd demo/chat_v2
cp .env.example .env
pip install -r requirements.txt
python backend.py
```

Start the frontend in another terminal:

```bash
cd demo/chat_v2/frontend
npm ci
npm run dev
```

Open `http://localhost:4000`. The backend listens on `http://localhost:8200`.

For Docker Compose, remote provider configuration, production notes, and the model-weight roadmap, see [deployment documentation](../../docs/DEPLOYMENT.md).

## Provider modes

- `local`: bundled mock or a local/self-hosted OpenAI-compatible endpoint.
- `custom`: any compatible remote chat-completions API.
- `heywhale`: the upstream HeyWhale integration.

Set `DATAPILOT_ALLOW_CLIENT_PROVIDER_CONFIG=false` for a public server that must enforce server-side provider settings.
