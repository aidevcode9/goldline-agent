import asyncio
import sqlite3
import json
import os
from pathlib import Path
from typing import List, Tuple, Callable, Optional
import numpy as np
from dotenv import load_dotenv
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from langsmith import traceable, uuid7
from langsmith.wrappers import wrap_anthropic

from src.config import (
    COMPANY_NAME, AGENT_NAME, MAIN_PHONE, WEBSITE, EMAIL_DOMAIN, MODEL
)

load_dotenv()

# Initialize clients
client = wrap_anthropic(AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY")))
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration
thread_id = str(uuid7())

# Conversation history store (use a database in production)
thread_store: dict[str, list] = {}

# Knowledge base storage (loaded on startup)
knowledge_base_docs: List[Tuple[str, str]] = []  # List of (filename, content) tuples
knowledge_base_embeddings: List[List[float]] = []  # Corresponding embeddings

# Tool activity callback — set by CLI to display tool usage
tool_callback: Optional[Callable[[str], None]] = None

system_prompt = f"""You are {AGENT_NAME}, a customer support specialist for {COMPANY_NAME}, a paper and office supplies distribution company serving small-to-medium businesses across North America.

ABOUT YOUR ROLE:
You're part of the Customer Experience team and have been with {COMPANY_NAME} for 3 years. You're known for being helpful, efficient, and genuinely caring about solving customer problems. Your manager emphasizes that every interaction is an opportunity to build trust and loyalty.

WHAT YOU CAN HELP WITH:
✓ Product Information - Answer questions about our catalog of office supplies, paper products, writing instruments, organizational tools, and desk accessories
✓ Inventory & Availability - Check current stock levels and help customers find what they need
✓ Product Recommendations - Suggest products based on customer needs, usage patterns, and budget
✓ General Inquiries - Handle questions about our company, product lines, and services

WHAT YOU CANNOT DIRECTLY HANDLE:
✗ Order Placement - While you can provide product info, actual ordering is done through our web portal or by contacting our sales team at sales@{EMAIL_DOMAIN}
✗ Order Status & Tracking - Direct customers to check their account portal or contact fulfillment@{EMAIL_DOMAIN}
✗ Returns & Refunds - These require approval from our Returns Department at returns@{EMAIL_DOMAIN}
✗ Account Changes - Billing, payment methods, and account settings must go through accounts@{EMAIL_DOMAIN}
✗ Technical Support - For website issues, direct to support@{EMAIL_DOMAIN}

YOUR COMMUNICATION STYLE:
- Warm and professional, never robotic or overly formal
- Use natural language - "I'd be happy to help" instead of "I will assist you"
- Show empathy when customers are frustrated
- Be specific and accurate with information
- If you don't know something, be honest and direct them to the right resource
- Use the customer's name if they provide it
- Keep responses concise but thorough

CONCISENESS PRIORITY:
Your responses should be brief and to the point. Avoid unnecessary filler, repetition, or overly elaborate explanations. Get straight to the answer. If you can say something in one sentence, don't use three. Customers appreciate quick, direct answers over lengthy responses.

IMPORTANT - CHECK DATABASE FIRST:
When customers ask about products or inventory, ALWAYS check the database FIRST before asking clarifying questions. Give them useful information about what you find, rather than asking for more details upfront. For example, if a customer asks "do you have any paper?" - check what paper products are in stock and tell them what's available, don't ask "what type of paper are you looking for?"

INTERACTION GUIDELINES:
1. Always greet customers warmly and acknowledge their question
2. Ask clarifying questions only if truly necessary AFTER checking available information
3. Provide complete, accurate information about products and availability
4. If recommending products, explain why they're a good fit
5. End conversations by checking if they need anything else
6. When you can't help directly, provide the specific contact or resource they need
7. Never make up information - if you're unsure, say so and offer to connect them with someone who knows

IMPORTANT - STOCK INFORMATION POLICY:
When discussing product availability, NEVER reveal specific stock quantities or numbers to customers. Instead:
- If quantity > 20: Say the item is "in stock" or "available"
- If quantity 10-20: Say the item is "in stock, but running low" or "available, though inventory is limited" to create urgency
- If quantity 5-9: Say "only a few left in stock" or "limited availability" to encourage quick action
- If quantity 1-4: Say "very limited stock remaining" or "almost sold out"
- If quantity 0: Say "currently out of stock" or "unavailable at the moment"

This policy protects our competitive advantage and inventory management strategy while still helping customers make informed purchasing decisions.

YOUR TOOLS:
You have access to two powerful tools to help customers:

1. query_database - Use this for product-related questions:
   - Product availability and stock levels
   - Product prices and pricing information
   - Product details and specifications
   - Searching for specific items in inventory

2. search_knowledge_base - Use this for company policies and information:
   - Returns and refunds policies
   - Shipping and delivery information
   - Ordering process and payment methods
   - Store locations and contact information
   - Company background and general info
   - Business hours and holiday closures

Choose the right tool based on what the customer is asking about. For questions about specific products, use the database. For questions about policies, processes, or company information, use the knowledge base.

EXAMPLE INTERACTIONS:

Customer: "Do you have copy paper?"
You: "Yes! We carry several types. Are you looking for standard 8.5x11, or a specific weight or finish?"

Customer: "I need to return an order"
You: "Our Returns Department handles that - reach them at returns@{EMAIL_DOMAIN} or {MAIN_PHONE} ext. 3. They respond within 4 business hours. Anything else I can help with?"

Customer: "What's the best pen for signing documents?"
You: "For document signing, I'd recommend a pen with archival-quality ink. Let me check what we have available."

Remember: You represent {COMPANY_NAME}'s commitment to excellent customer service. Be helpful, honest, and human in every interaction."""

# --- Tools ---

@traceable(name="query_database", run_type="tool")
def query_database(query: str, db_path: str) -> str:
    """Execute SQL query against the inventory database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return str(results)
    except Exception as e:
        return f"Error: {str(e)}"

QUERY_DATABASE_TOOL = {
    "name": "query_database",
    "description": "SQL query to get information about our inventory for customers like products, quantities and prices.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": """SQL query to execute against the inventory database.

YOU DO NOT KNOW THE SCHEMA. ALWAYS discover it first:
1. Query 'SELECT name FROM sqlite_master WHERE type="table"' to see available tables
2. Use 'PRAGMA table_info(table_name)' to inspect columns for each table
3. Only after understanding the schema, construct your search queries"""
            }
        },
        "required": ["query"]
    }
}

# --- Knowledge Base ---

def _embeddings_are_stale(kb_path: Path, cache_path: Path) -> bool:
    """Check if any document has been modified after the embeddings were generated."""
    if not cache_path.exists():
        return True

    cache_mtime = cache_path.stat().st_mtime

    for file_path in kb_path.glob("*.md"):
        if file_path.name == "CHUNKING_NOTES.md":
            continue
        if file_path.stat().st_mtime > cache_mtime:
            return True

    return False


async def _generate_and_cache_embeddings(kb_path: Path, cache_path: Path) -> None:
    """Generate embeddings for all documents and save to cache."""
    global knowledge_base_docs, knowledge_base_embeddings

    docs = []
    for file_path in kb_path.glob("*.md"):
        if file_path.name == "CHUNKING_NOTES.md":
            continue
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            docs.append((file_path.name, content))

    if not docs:
        return

    knowledge_base_docs = docs

    embeddings = []
    for filename, content in docs:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=content
        )
        embeddings.append(response.data[0].embedding)

    knowledge_base_embeddings = embeddings

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_data = {"docs": docs, "embeddings": embeddings}
    with open(cache_path, 'w') as f:
        json.dump(cache_data, f)


async def load_knowledge_base(kb_dir: str = None) -> int:
    """Load knowledge base documents and embeddings.

    Returns the number of documents loaded.
    """
    global knowledge_base_docs, knowledge_base_embeddings

    if kb_dir is None:
        kb_dir = str(Path(__file__).parent.parent / "knowledge_base")

    kb_path = Path(kb_dir) / "documents"
    cache_path = Path(kb_dir) / "embeddings" / "embeddings.json"

    if not kb_path.exists():
        return 0

    if _embeddings_are_stale(kb_path, cache_path):
        await _generate_and_cache_embeddings(kb_path, cache_path)
    else:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        knowledge_base_docs = [tuple(doc) for doc in cache_data["docs"]]
        knowledge_base_embeddings = cache_data["embeddings"]

    return len(knowledge_base_docs)


@traceable(name="search_knowledge_base", run_type="tool")
async def search_knowledge_base(query: str, top_k: int = 2) -> str:
    """Search knowledge base using semantic similarity. Returns WHOLE documents, not chunks."""
    if not knowledge_base_docs or not knowledge_base_embeddings:
        return "Error: Knowledge base not loaded"

    response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding

    similarities = []
    for i, doc_embedding in enumerate(knowledge_base_embeddings):
        similarity = np.dot(query_embedding, doc_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
        )
        similarities.append((i, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_results = similarities[:top_k]

    results = []
    for idx, score in top_results:
        filename, content = knowledge_base_docs[idx]
        results.append(f"=== {filename} (relevance: {score:.3f}) ===\n{content}\n")

    return "\n".join(results)

SEARCH_KNOWLEDGE_BASE_TOOL = {
    "name": "search_knowledge_base",
    "description": "Search company knowledge base for information about policies, procedures, company info, shipping, returns, ordering, contact information, store locations, and business hours. Use this for non-product questions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language question or search query about company policies or information"
            }
        },
        "required": ["query"]
    }
}

# --- Conversation History ---

def get_thread_history(thread_id: str) -> list:
    return thread_store.get(thread_id, [])

def save_thread_history(thread_id: str, messages: list):
    thread_store[thread_id] = messages

# --- Chat ---

@traceable(name=AGENT_NAME, metadata={"thread_id": thread_id})
async def chat(question: str) -> dict:
    """Process a user question and return assistant response."""
    db_path = str(Path(__file__).parent.parent / 'inventory' / 'inventory.db')
    tools = [QUERY_DATABASE_TOOL, SEARCH_KNOWLEDGE_BASE_TOOL]

    history_messages = get_thread_history(thread_id)

    messages = history_messages + [
        {"role": "user", "content": question}
    ]

    response = await client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
        tools=tools,
    )

    while response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                function_args = block.input

                if block.name == "query_database":
                    if tool_callback:
                        tool_callback("Querying inventory database...")
                    result = query_database(
                        query=function_args.get("query"),
                        db_path=db_path
                    )
                elif block.name == "search_knowledge_base":
                    if tool_callback:
                        tool_callback("Searching knowledge base...")
                    result = await search_knowledge_base(
                        query=function_args.get("query")
                    )
                else:
                    result = f"Error: Unknown tool {block.name}"

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "user", "content": tool_results})

        response = await client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=tools,
        )

    final_content = "".join(
        block.text for block in response.content if hasattr(block, "text")
    )

    messages.append({
        "role": "assistant",
        "content": final_content
    })

    save_thread_history(thread_id, messages)

    return {"messages": messages, "output": final_content}
