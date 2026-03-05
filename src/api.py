"""GoldLine Agent — FastAPI backend with SSE streaming."""

import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from src import agent
from src.config import COMPANY_NAME, AGENT_NAME
from src.history import new_thread_id

logger = logging.getLogger(__name__)

app = FastAPI(
    title=f"{COMPANY_NAME} Agent API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    result = await agent.chat(req.message)
    return {"response": result["output"], "thread_id": agent.thread_id}


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
