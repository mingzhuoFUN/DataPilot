"""Run the web, API, mock provider, and gateway in one deployable container."""

from __future__ import annotations

import os
import base64
import hashlib
import signal
import subprocess
import sys
import time


PROCESSES: list[subprocess.Popen] = []


def _configure_gateway_auth() -> None:
    password = os.getenv("DATAPILOT_SITE_PASSWORD", "").strip()
    config_path = "/etc/nginx/conf.d/default.conf"
    config = open(config_path, encoding="utf-8").read()
    marker = "# DATAPILOT_AUTH"
    if not password:
        config = config.replace(marker, "")
    else:
        username = os.getenv("DATAPILOT_SITE_USERNAME", "datapilot").strip() or "datapilot"
        password_hash = base64.b64encode(hashlib.sha1(password.encode("utf-8")).digest()).decode("ascii")
        with open("/etc/nginx/.htpasswd", "w", encoding="utf-8") as password_file:
            password_file.write(f"{username}:{{SHA}}{password_hash}\n")
        config = config.replace(
            marker,
            'auth_basic "DataPilot Preview";\n    auth_basic_user_file /etc/nginx/.htpasswd;',
        )
    with open(config_path, "w", encoding="utf-8") as config_file:
        config_file.write(config)


def _start(command: list[str], cwd: str, env: dict[str, str] | None = None) -> None:
    process = subprocess.Popen(command, cwd=cwd, env=env)
    PROCESSES.append(process)
    print(f"started pid={process.pid}: {' '.join(command)}", flush=True)


def _shutdown(signum: int | None = None, frame: object | None = None) -> None:
    if signum is not None:
        print(f"received signal {signum}; stopping services", flush=True)
    for process in reversed(PROCESSES):
        if process.poll() is None:
            process.terminate()
    deadline = time.monotonic() + 10
    for process in reversed(PROCESSES):
        if process.poll() is not None:
            continue
        try:
            process.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> int:
    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    frontend_env = os.environ.copy()
    frontend_env.update({"PORT": "4000", "HOSTNAME": "0.0.0.0"})

    _configure_gateway_auth()
    provider = os.getenv("DATAPILOT_MODEL_PROVIDER", "local").strip().lower()
    api_base = os.getenv("DATAPILOT_MODEL_API_BASE", "").strip().lower()
    if provider == "local" and ("127.0.0.1:8000" in api_base or "localhost:8000" in api_base):
        _start([sys.executable, "start_mock_vllmserver.py"], "/app/mock")
    _start([sys.executable, "backend.py"], "/app/backend")
    _start(["node", "server.js"], "/app/frontend", frontend_env)
    _start(["nginx", "-g", "daemon off;"], "/app")

    try:
        while True:
            for process in PROCESSES:
                return_code = process.poll()
                if return_code is not None:
                    print(f"service pid={process.pid} exited with code {return_code}", flush=True)
                    return return_code or 1
            time.sleep(0.5)
    finally:
        _shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
