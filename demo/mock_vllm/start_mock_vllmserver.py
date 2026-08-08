"""Small OpenAI-compatible streaming server for DataPilot development.

This intentionally returns a deterministic structured response. It lets the
complete browser/backend pipeline run without downloading model weights.
"""

from __future__ import annotations

import http.server
import json
import time
from typing import Any


FULL_RESPONSE_TEXT = """<Analyze>
The request and selected workspace files reached the model provider correctly.
This development response is deterministic and does not perform real inference.
</Analyze>
<Answer>
DataPilot's upload, streaming, structured-section parsing, and report pipeline are connected. Configure a real OpenAI-compatible endpoint for genuine analysis.
</Answer>"""


class MockVLLMHandler(http.server.BaseHTTPRequestHandler):
    server_version = "DataPilotMock/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_stream(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        chunk_id = f"chatcmpl-mock-{int(time.time() * 1000)}"
        for part in (FULL_RESPONSE_TEXT[index:index + 12] for index in range(0, len(FULL_RESPONSE_TEXT), 12)):
            payload = {
                "id": chunk_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "DeepAnalyze-8B",
                "choices": [{"index": 0, "delta": {"content": part}, "finish_reason": None}],
            }
            self.wfile.write(f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8"))
            self.wfile.flush()
            time.sleep(0.01)

        final_payload = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "DeepAnalyze-8B",
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        self.wfile.write(f"data: {json.dumps(final_payload)}\n\ndata: [DONE]\n\n".encode("utf-8"))
        self.wfile.flush()
        self.close_connection = True

    def do_POST(self) -> None:
        if self.path == "/v1/chat/completions":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                request = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except (ValueError, json.JSONDecodeError) as exc:
                self._send_json(400, {"error": str(exc)})
                return

            if request.get("stream"):
                self._send_stream()
                return
            self._send_json(
                200,
                {
                    "id": f"chatcmpl-mock-{int(time.time() * 1000)}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "DeepAnalyze-8B",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": FULL_RESPONSE_TEXT},
                            "finish_reason": "stop",
                        }
                    ],
                },
            )
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "healthy", "service": "DataPilot mock provider"})
        elif self.path == "/v1/models":
            self._send_json(
                200,
                {
                    "object": "list",
                    "data": [{"id": "DeepAnalyze-8B", "object": "model", "owned_by": "ruc-datalab"}],
                },
            )
        else:
            self._send_json(404, {"error": "Endpoint not found"})


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = http.server.ThreadingHTTPServer((host, port), MockVLLMHandler)
    print(f"DataPilot mock provider listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
