"""Run the web, API, mock provider, and gateway in one deployable container."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time


PROCESSES: list[subprocess.Popen] = []


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
