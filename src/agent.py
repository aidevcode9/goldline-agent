"""GoldLine Agent — chat orchestration."""

import logging
import os
from pathlib import Path
from typing import Callable, Optional

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
