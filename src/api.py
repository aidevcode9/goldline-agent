"""GoldLine Agent — FastAPI backend with SSE streaming."""

import json
import logging
import os
import re

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from src import agent
from src.config import COMPANY_NAME, AGENT_NAME, QUOTE_OUTPUT_DIR
from src.history import new_thread_id

logger = logging.getLogger(__name__)

app = FastAPI(
    title=f"{COMPANY_NAME} Agent API",
    version="1.0.0",
)

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

_kb_loaded = False


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


@app.on_event("startup")
async def startup():
    global _kb_loaded
    doc_count = await agent.load_knowledge_base()
    _kb_loaded = True
    logger.info("Knowledge base loaded: %d documents", doc_count)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "agent": AGENT_NAME,
        "kb_loaded": _kb_loaded,
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    """Non-streaming chat endpoint."""
    tid = req.thread_id or new_thread_id()
    result = await agent.chat(req.message, tid=tid)
    return {"response": result["output"], "thread_id": result["thread_id"]}


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """SSE streaming endpoint with trace events for the Reasoning View."""
    tid = req.thread_id or new_thread_id()

    async def event_generator():
        async for event in agent.chat_stream(req.message, tid=tid):
            yield {
                "event": event["event"],
                "data": json.dumps(event["data"]),
            }

    return EventSourceResponse(event_generator())


_QUOTE_FILENAME_RE = re.compile(r"^GQ-\d{8}-\d{4}\.pdf$")


@app.get("/quotes/{filename}")
async def download_quote(filename: str):
    """Serve a generated quote PDF."""
    safe_name = Path(filename).name
    if not _QUOTE_FILENAME_RE.match(safe_name):
        raise HTTPException(status_code=404, detail="Quote not found")
    file_path = (Path(QUOTE_OUTPUT_DIR) / safe_name).resolve()
    if not str(file_path).startswith(str(Path(QUOTE_OUTPUT_DIR).resolve())):
        raise HTTPException(status_code=404, detail="Quote not found")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Quote not found")
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=safe_name,
    )
