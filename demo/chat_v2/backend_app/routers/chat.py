from __future__ import annotations

import json

from fastapi import APIRouter, Body, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from ..services.chat import bot_stream, build_chat_runtime_config, request_stop
from ..services.execution import execute_code_safe
from ..services.workspace import get_session_workspace
from ..settings import settings


router = APIRouter()


@router.post("/execute")
async def execute_code_api(request: dict):
    code = request.get("code", "")
    session_id = request.get("session_id", "default")
    workspace_dir = get_session_workspace(session_id)

    if not code:
        return {
            "success": False,
            "result": "Error: No code provided",
            "message": "Code execution failed",
        }

    try:
        result = await run_in_threadpool(execute_code_safe, code, workspace_dir, session_id)
        return {
            "success": True,
            "result": result,
            "message": "Code executed successfully",
        }
    except Exception as exc:
        return {
            "success": False,
            "result": f"Error: {exc}",
            "message": "Code execution failed",
        }


@router.post("/chat/completions")
async def chat(body: dict = Body(...)):
    messages = body.get("messages", [])
    workspace = body.get("workspace", [])
    session_id = body.get("session_id", "default")
    try:
        runtime_config = build_chat_runtime_config(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    def generate():
        try:
            stream = bot_stream(messages, workspace, session_id, runtime_config)
            for delta_content in stream:
                chunk = {
                    "id": "chatcmpl-stream",
                    "object": "chat.completion.chunk",
                    "created": 1677652288,
                    "model": runtime_config.model or settings.model_path,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": delta_content},
                            "finish_reason": None,
                        }
                    ],
                }
                yield json.dumps(chunk) + "\n"
        except Exception as exc:
            error_text = str(exc)
            if "exceeds the available context size" in error_text or "exceed_context_size" in error_text:
                message = (
                    "\n<Answer>\n本地模型上下文已满，分析已停止。"
                    "请清空较早对话后重试，或将本地模型上下文调大/改用 API 模型。\n</Answer>"
                )
            elif "timed out" in error_text.lower() or "timeout" in error_text.lower():
                message = "\n<Answer>\n模型响应超时，分析已停止。请重试或检查模型/API 服务。\n</Answer>"
            else:
                message = f"\n<Answer>\n模型调用失败，分析已停止：{error_text}\n</Answer>"
            chunk = {
                "id": "chatcmpl-stream",
                "object": "chat.completion.chunk",
                "created": 1677652288,
                "model": runtime_config.model or settings.model_path,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": message},
                        "finish_reason": None,
                    }
                ],
            }
            yield json.dumps(chunk) + "\n"

        end_chunk = {
            "id": "chatcmpl-stream",
            "object": "chat.completion.chunk",
            "created": 1677652288,
            "model": runtime_config.model or settings.model_path,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield json.dumps(end_chunk) + "\n"

    return StreamingResponse(generate(), media_type="text/plain")


@router.post("/chat/stop")
async def stop_chat(body: dict = Body(default={})):
    session_id = body.get("session_id", "default")
    request_stop(session_id)
    return {"message": "stop requested", "session_id": session_id}
