"""GoldLine Agent — chat orchestration."""

import json
import logging
import os
import time
from pathlib import Path
from typing import AsyncGenerator, Callable, Optional

from dotenv import load_dotenv
from anthropic import AsyncAnthropic, APIError
from anthropic.types import TextBlock
from openai import AsyncOpenAI
from langsmith import traceable
from langsmith.wrappers import wrap_anthropic

from src.config import AGENT_NAME, MODEL
from src.history import new_thread_id, get_messages, save_messages
from src.knowledge import KnowledgeBase
from src.prompts import build_system_prompt
from src.tools import ALL_TOOLS, execute_tool

load_dotenv()

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 10
MAX_HISTORY_MESSAGES = 100

# Clients
client = wrap_anthropic(AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY")))
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# State
thread_id = new_thread_id()
knowledge_base = KnowledgeBase(openai_client)
system_prompt = build_system_prompt()

# Tool activity callback — set by CLI to display tool usage
tool_callback: Optional[Callable[[str], None]] = None


async def load_knowledge_base(kb_dir: str = None) -> int:
    """Load knowledge base documents. Returns document count."""
    return await knowledge_base.load(kb_dir)


def _truncate_history(messages: list) -> list:
    """Keep only the most recent messages to avoid exceeding context limits."""
    if len(messages) <= MAX_HISTORY_MESSAGES:
        return messages
    return messages[-MAX_HISTORY_MESSAGES:]


@traceable(name=AGENT_NAME, metadata={"thread_id": thread_id})
async def chat(question: str) -> dict:
    """Process a user question and return assistant response."""
    db_path = str(Path(__file__).parent.parent / "inventory" / "inventory.db")

    history = _truncate_history(get_messages(thread_id))
    messages = history + [{"role": "user", "content": question}]

    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=ALL_TOOLS,
        )
    except APIError:
        logger.exception("Anthropic API error")
        return {"messages": messages, "output": "I'm having trouble connecting right now. Please try again in a moment."}

    iterations = 0
    while response.stop_reason == "tool_use" and iterations < MAX_TOOL_ITERATIONS:
        iterations += 1
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = await execute_tool(
                    block.name,
                    block.input,
                    db_path=db_path,
                    knowledge_base=knowledge_base,
                    on_tool_call=tool_callback,
                )
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )

        messages.append({"role": "user", "content": tool_results})

        try:
            response = await client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=ALL_TOOLS,
            )
        except APIError:
            logger.exception("Anthropic API error during tool loop")
            return {"messages": messages, "output": "I'm having trouble connecting right now. Please try again in a moment."}

    if iterations >= MAX_TOOL_ITERATIONS:
        logger.warning("Tool loop hit max iterations (%d)", MAX_TOOL_ITERATIONS)
        final_content = "I'm sorry, I wasn't able to complete your request. Could you try rephrasing your question?"
    else:
        final_content = "".join(
            block.text for block in response.content if isinstance(block, TextBlock)
        )

    messages.append({"role": "assistant", "content": final_content})
    save_messages(thread_id, messages)

    return {"messages": messages, "output": final_content}


async def chat_stream(
    question: str, tid: str | None = None
) -> AsyncGenerator[dict, None]:
    """Streaming version of chat() that yields trace events for the Reasoning View.

    Events:
        thinking  — agent is processing
        tool_call — tool invoked with input
        tool_result — tool returned with result + latency
        text — final response text
        done — summary with totals
        error — something went wrong
    """
    tid = tid or thread_id
    db_path = str(Path(__file__).parent.parent / "inventory" / "inventory.db")
    request_start = time.monotonic()
    total_input_tokens = 0
    total_output_tokens = 0
    tool_call_count = 0

    history = _truncate_history(get_messages(tid))
    messages = history + [{"role": "user", "content": question}]

    yield {"event": "thinking", "data": {"status": "Processing your question..."}}

    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=ALL_TOOLS,
        )
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens
    except APIError:
        logger.exception("Anthropic API error")
        yield {"event": "error", "data": {"message": "I'm having trouble connecting right now. Please try again in a moment."}}
        return

    iterations = 0
    while response.stop_reason == "tool_use" and iterations < MAX_TOOL_ITERATIONS:
        iterations += 1
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_call_count += 1

                yield {
                    "event": "tool_call",
                    "data": {
                        "tool": block.name,
                        "input": block.input,
                        "iteration": iterations,
                    },
                }

                tool_start = time.monotonic()
                result = await execute_tool(
                    block.name,
                    block.input,
                    db_path=db_path,
                    knowledge_base=knowledge_base,
                )
                tool_latency = round((time.monotonic() - tool_start) * 1000)

                yield {
                    "event": "tool_result",
                    "data": {
                        "tool": block.name,
                        "result": result[:500],  # truncate for UI
                        "latency_ms": tool_latency,
                    },
                }

                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result}
                )

        messages.append({"role": "user", "content": tool_results})

        yield {"event": "thinking", "data": {"status": "Analyzing results..."}}

        try:
            response = await client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=ALL_TOOLS,
            )
            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens
        except APIError:
            logger.exception("Anthropic API error during tool loop")
            yield {"event": "error", "data": {"message": "I'm having trouble connecting right now. Please try again in a moment."}}
            return

    if iterations >= MAX_TOOL_ITERATIONS:
        final_content = "I'm sorry, I wasn't able to complete your request. Could you try rephrasing your question?"
    else:
        final_content = "".join(
            block.text for block in response.content if isinstance(block, TextBlock)
        )

    messages.append({"role": "assistant", "content": final_content})
    save_messages(tid, messages)

    yield {"event": "text", "data": {"content": final_content}}

    total_latency = round((time.monotonic() - request_start) * 1000)
    yield {
        "event": "done",
        "data": {
            "total_latency_ms": total_latency,
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "tool_calls": tool_call_count,
        },
    }
