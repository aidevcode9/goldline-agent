"""GoldLine Agent — Rich CLI Interface."""
import asyncio
import sys

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

from src import agent
from src.config import COMPANY_NAME, AGENT_NAME, BRAND_COLOR, ACCENT_COLOR, TAGLINE

console = Console()


def show_banner(doc_count: int):
    """Display startup banner."""
    title = Text()
    title.append("★  ", style=f"bold {BRAND_COLOR}")
    title.append(COMPANY_NAME.upper(), style=f"bold {BRAND_COLOR}")
    title.append("  ★", style=f"bold {BRAND_COLOR}")

    lines = Text()
    lines.append(f"{TAGLINE}\n\n", style=f"italic {ACCENT_COLOR}")
    lines.append(f"AI Customer Support  ·  Powered by Claude\n\n", style="dim")
    lines.append(f"Thread:  ", style="dim")
    lines.append(f"{agent.thread_id}\n", style="cyan")
    lines.append(f"LangSmith tracing:  ", style="dim")
    lines.append(f"enabled\n", style="green")
    lines.append(f"Knowledge base:  ", style="dim")
    lines.append(f"{doc_count} documents loaded", style="green")

    console.print()
    console.print(Panel(
        lines,
        title=title,
        border_style=BRAND_COLOR,
        padding=(1, 3),
    ))
    console.print()
    console.print(f"  Type your question, or [bold]quit[/bold] to exit.\n", style="dim")


def show_goodbye(message_count: int):
    """Display exit summary."""
    console.print()
    console.print(
        f"  Thanks for chatting with {COMPANY_NAME}! Goodbye.",
        style=f"bold {BRAND_COLOR}"
    )
    console.print(
        f"  Session: {agent.thread_id[:8]}  ·  Messages: {message_count}  ·  Traced to LangSmith",
        style="dim"
    )
    console.print()


def on_tool_call(tool_name: str):
    """Display tool activity indicator."""
    console.print(f"  ⚡ {tool_name}", style=f"italic {ACCENT_COLOR}")


async def run():
    """Main chat loop."""
    # Wire up tool callback
    agent.tool_callback = on_tool_call

    # Load knowledge base
    with console.status(f"[{BRAND_COLOR}]Loading knowledge base...", spinner="dots"):
        doc_count = await agent.load_knowledge_base()

    show_banner(doc_count)

    message_count = 0
    while True:
        try:
            user_input = console.input(f"[bold {BRAND_COLOR}]You ▸[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            show_goodbye(message_count)
            break

        if user_input.lower() in ('quit', 'exit', 'q'):
            show_goodbye(message_count)
            break

        if not user_input:
            continue

        with console.status(f"[{BRAND_COLOR}]{AGENT_NAME} is thinking...", spinner="dots"):
            result = await agent.chat(user_input)

        md = Markdown(result["output"])
        console.print(Panel(
            md,
            title=f"[bold {BRAND_COLOR}]{AGENT_NAME}",
            border_style=ACCENT_COLOR,
            padding=(1, 2),
        ))
        console.print()
        message_count += 1


def main():
    """Entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
