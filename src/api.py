"""GoldLine Agent — FastAPI backend with SSE streaming."""

import json
import logging
import os
import re
import secrets
import time
from collections import defaultdict

from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from src import agent
from src.config import COMPANY_NAME, AGENT_NAME, QUOTE_OUTPUT_DIR
from src.history import new_thread_id

logger = logging.getLogger(__name__)

# --- Auth ---
_API_SECRET = os.getenv("API_SECRET_KEY", "")


def _verify_api_key(request: Request) -> None:
    """Verify Bearer token on protected endpoints."""
    if not _API_SECRET:
        return  # auth disabled when no key configured (local dev)
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer ") or not secrets.compare_digest(auth[7:], _API_SECRET):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# --- Rate limiting (in-memory, per-IP) ---
_RATE_WINDOW = 60  # seconds
_RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "20"))
_rate_log: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(request: Request) -> None:
    """Simple sliding-window rate limiter per client IP."""
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = _rate_log[ip]
    # Prune old entries
    _rate_log[ip] = [t for t in window if now - t < _RATE_WINDOW]
    if len(_rate_log[ip]) >= _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again shortly.")
    _rate_log[ip].append(now)


app = FastAPI(
    title=f"{COMPANY_NAME} Agent API",
    version="1.0.0",
)

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

_kb_loaded = False

_MAX_MESSAGE_LEN = 4000


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=_MAX_MESSAGE_LEN)
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


@app.post("/chat", dependencies=[Depends(_verify_api_key), Depends(_check_rate_limit)])
async def chat(req: ChatRequest):
    """Non-streaming chat endpoint."""
    tid = req.thread_id or new_thread_id()
    result = await agent.chat(req.message, tid=tid)
    return {"response": result["output"], "thread_id": result["thread_id"]}


@app.post("/chat/stream", dependencies=[Depends(_verify_api_key), Depends(_check_rate_limit)])
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


_QUOTE_FILENAME_RE = re.compile(r"^GQ-\d{8}-[A-F0-9]{8}\.pdf$")


@app.get("/quotes/{filename}", dependencies=[Depends(_verify_api_key)])
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
