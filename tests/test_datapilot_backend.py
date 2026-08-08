from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAT_V2 = ROOT / "demo" / "chat_v2"
sys.path.insert(0, str(CHAT_V2))


def test_session_id_is_sanitized(tmp_path, monkeypatch):
    from backend_app.services import workspace

    monkeypatch.setattr(
        workspace,
        "settings",
        replace(workspace.settings, workspace_base_dir=str(tmp_path)),
    )
    resolved = Path(workspace.get_session_workspace("../../private data")).resolve()

    assert resolved.parent == tmp_path.resolve()
    assert resolved.name == "private-data"


def test_generated_code_does_not_receive_server_secrets(tmp_path, monkeypatch):
    from backend_app.services import execution

    monkeypatch.setenv("DATAPILOT_MODEL_API_KEY", "must-not-leak")
    result = execution.execute_code_safe(
        "import os; print(os.getenv('DATAPILOT_MODEL_API_KEY', 'redacted'))",
        str(tmp_path),
    )

    assert result.strip() == "redacted"


def test_server_side_provider_configuration_can_be_locked(monkeypatch):
    from backend_app.services import chat

    locked_settings = replace(
        chat.settings,
        allow_client_provider_config=False,
        default_provider="custom",
        api_base="https://models.example.test/v1",
        model_path="portfolio-model",
        model_api_key="server-secret",
    )
    monkeypatch.setattr(chat, "settings", locked_settings)

    config = chat.build_chat_runtime_config(
        {
            "provider": "custom",
            "api_base": "https://attacker.invalid/v1",
            "model": "untrusted-model",
            "api_key": "browser-key",
        }
    )

    assert config.provider == "custom"
    assert config.api_base == "https://models.example.test/v1"
    assert config.model == "portfolio-model"
    assert config.api_key == "server-secret"


def test_health_endpoint():
    import asyncio

    from backend_app.app import create_app

    app = create_app()
    health_route = next(
        route for route in app.routes if getattr(route, "path", None) == "/health"
    )
    payload = asyncio.run(health_route.endpoint())

    assert payload["status"] == "ok"
    assert payload["service"] == "DataPilot API"
