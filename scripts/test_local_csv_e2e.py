"""Run a real CSV analysis through the same /api routes used by the web UI."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx


BASE_URL = "http://127.0.0.1:4000/api"
SESSION_ID = "csv-e2e-validation"
CSV_CONTENT = """product,quantity,unit_price
Notebook,3,5200
Monitor,5,1800
Keyboard,8,450
Notebook,2,5100
Monitor,1,1750
"""


def main() -> int:
    with httpx.Client(base_url=BASE_URL, timeout=240.0, trust_env=False) as client:
        client.post("/workspace/clear", params={"session_id": SESSION_ID}).raise_for_status()

        upload = client.post(
            "/workspace/upload",
            params={"session_id": SESSION_ID},
            files={"files": ("sales.csv", CSV_CONTENT.encode("utf-8"), "text/csv")},
        )
        upload.raise_for_status()
        uploaded = upload.json()
        if not uploaded.get("files"):
            raise RuntimeError(f"CSV upload failed: {uploaded}")

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Use Python to read sales.csv. First calculate row revenue as "
                        "quantity * unit_price, then GROUP ALL ROWS BY product and SUM "
                        "their revenue. Identify the product with the highest aggregated "
                        "revenue and save the grouped table as product_revenue_summary.csv. "
                        "You must execute code and report the exact aggregated value before "
                        "the final answer."
                    ),
                }
            ],
            "workspace": ["sales.csv"],
            "session_id": SESSION_ID,
            "stream": True,
        }

        chunks: list[str] = []
        with client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                event = json.loads(line)
                delta = event.get("choices", [{}])[0].get("delta", {}).get("content")
                if delta:
                    chunks.append(delta)

        output = "".join(chunks)
        if "<Execute>" not in output or "<Answer>" not in output:
            raise RuntimeError(f"Structured analysis was incomplete:\n{output}")
        normalized_output = output.replace(",", "")
        if "Notebook" not in output or "25800" not in normalized_output:
            raise RuntimeError(f"The aggregated revenue result was incorrect:\n{output}")

        files_response = client.get("/workspace/files", params={"session_id": SESSION_ID})
        files_response.raise_for_status()
        files = files_response.json().get("files", [])
        reports = [item for item in files if "Answer_Report_" in item.get("name", "")]
        if not reports:
            raise RuntimeError(f"No generated Markdown report found: {files}")

        print("OK: CSV uploaded through frontend proxy")
        print("OK: DeepAnalyze executed Python and returned a structured answer")
        print(f"OK: generated report {reports[-1]['path']}")
        print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        raise
