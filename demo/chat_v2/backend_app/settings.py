from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


os.environ.setdefault("MPLBACKEND", "Agg")


def _load_demo_env() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _get_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env(primary: str, legacy: str, default: str = "") -> str:
    return os.getenv(primary, os.getenv(legacy, default))


def _get_csv_env(name: str, default: str) -> tuple[str, ...]:
    value = os.getenv(name, default)
    return tuple(item.strip() for item in value.split(",") if item.strip())


_load_demo_env()


CHINESE_MATPLOTLIB_BOOTSTRAP = """
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
"""


PREVIEWABLE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".pdf",
    ".txt",
    ".doc",
    ".docx",
    ".csv",
    ".xlsx",
}


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "DataPilot API"
    app_version: str = "0.1.0"
    api_base: str = _env("DATAPILOT_MODEL_API_BASE", "DEEPANALYZE_API_BASE", "http://localhost:8000/v1")
    model_path: str = _env("DATAPILOT_MODEL_NAME", "DEEPANALYZE_MODEL_PATH", "DeepAnalyze-8B")
    model_api_key: str = os.getenv("DATAPILOT_MODEL_API_KEY", "")
    default_provider: str = os.getenv("DATAPILOT_MODEL_PROVIDER", "local").strip().lower()
    allow_client_provider_config: bool = _get_bool_env("DATAPILOT_ALLOW_CLIENT_PROVIDER_CONFIG", True)
    workspace_base_dir: str = _env("DATAPILOT_WORKSPACE_BASE", "DEEPANALYZE_WORKSPACE_BASE", "workspace")
    http_server_host: str = _env("DATAPILOT_FILE_SERVER_HOST", "DEEPANALYZE_FILE_SERVER_HOST", "localhost")
    http_server_port: int = int(_env("DATAPILOT_FILE_SERVER_PORT", "DEEPANALYZE_FILE_SERVER_PORT", "8100"))
    backend_host: str = _env("DATAPILOT_BACKEND_HOST", "DEEPANALYZE_BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(_env("DATAPILOT_BACKEND_PORT", "DEEPANALYZE_BACKEND_PORT", "8200"))
    cors_origins: tuple[str, ...] = _get_csv_env(
        "DATAPILOT_CORS_ORIGINS",
        "http://localhost:4000,http://127.0.0.1:4000",
    )
    max_upload_mb: int = int(os.getenv("DATAPILOT_MAX_UPLOAD_MB", "50"))
    allow_external_proxy: bool = _get_bool_env("DATAPILOT_ALLOW_EXTERNAL_PROXY", False)
    execution_mode: str = _env("DATAPILOT_EXECUTION_MODE", "DEEPANALYZE_EXECUTION_MODE", "local")
    execution_timeout_sec: int = int(_env("DATAPILOT_EXECUTION_TIMEOUT_SEC", "DEEPANALYZE_EXECUTION_TIMEOUT_SEC", "120"))
    docker_image: str = _env("DATAPILOT_DOCKER_IMAGE", "DEEPANALYZE_DOCKER_IMAGE", "datapilot-exec:latest")
    docker_container_name: str = os.getenv(
        "DATAPILOT_DOCKER_CONTAINER_NAME",
        os.getenv("DEEPANALYZE_DOCKER_CONTAINER_NAME", "datapilot-exec"),
    )
    docker_session_idle_ttl_sec: int = int(
        _env("DATAPILOT_DOCKER_SESSION_IDLE_TTL_SEC", "DEEPANALYZE_DOCKER_SESSION_IDLE_TTL_SEC", "1800")
    )
    docker_workspace_dir: str = _env("DATAPILOT_DOCKER_WORKSPACE_DIR", "DEEPANALYZE_DOCKER_WORKSPACE_DIR", "/workspace")
    docker_python_bin: str = _env("DATAPILOT_DOCKER_PYTHON_BIN", "DEEPANALYZE_DOCKER_PYTHON_BIN", "python")
    docker_stop_on_shutdown: bool = _get_bool_env(
        "DATAPILOT_DOCKER_STOP_ON_SHUTDOWN",
        True,
    )
    pdf_cjk_mainfont: str = _env("DATAPILOT_PDF_CJK_MAINFONT", "DEEPANALYZE_PDF_CJK_MAINFONT", "").strip()
    pdf_auto_download_pandoc: bool = _get_bool_env(
        "DATAPILOT_PDF_AUTO_DOWNLOAD_PANDOC",
        True,
    )
    pdf_pandoc_cache_dir: str = _env(
        "DATAPILOT_PDF_PANDOC_CACHE_DIR",
        "DEEPANALYZE_PDF_PANDOC_CACHE_DIR",
        "",
    ).strip()

    @property
    def file_server_base(self) -> str:
        return f"http://{self.http_server_host}:{self.http_server_port}"

    @property
    def use_docker_execution(self) -> bool:
        return self.execution_mode.strip().lower() == "docker"


settings = Settings()
