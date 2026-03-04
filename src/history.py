"""Conversation history management."""

from langsmith import uuid7

# In-memory thread store (use a database in production)
_thread_store: dict[str, list] = {}


def new_thread_id() -> str:
    """Generate a new unique thread ID."""
    return str(uuid7())


def get_messages(thread_id: str) -> list:
    """Retrieve conversation history for a thread."""
    return _thread_store.get(thread_id, [])


def save_messages(thread_id: str, messages: list) -> None:
    """Save conversation history for a thread."""
    _thread_store[thread_id] = messages
