"""Knowledge base — document loading, embedding, and semantic search."""

import json
from pathlib import Path
from typing import List, Tuple

import numpy as np
from langsmith import traceable
from openai import AsyncOpenAI

from src.config import EMBEDDING_MODEL, KB_RELEVANCE_THRESHOLD, KB_TOP_K


class KnowledgeBase:
    """Manages document embeddings and semantic search."""

    def __init__(self, openai_client: AsyncOpenAI):
        self._client = openai_client
        self.docs: List[Tuple[str, str]] = []
        self.embeddings: List[List[float]] = []

    async def load(self, kb_dir: str = None) -> int:
        """Load documents and embeddings. Returns document count."""
        if kb_dir is None:
            kb_dir = str(Path(__file__).parent.parent / "knowledge_base")

        kb_path = Path(kb_dir) / "documents"
        cache_path = Path(kb_dir) / "embeddings" / "embeddings.json"

        if not kb_path.exists():
            return 0

        if self._embeddings_are_stale(kb_path, cache_path):
            await self._generate_and_cache(kb_path, cache_path)
        else:
            with open(cache_path, "r") as f:
                cache_data = json.load(f)
            self.docs = [tuple(doc) for doc in cache_data["docs"]]
            self.embeddings = cache_data["embeddings"]

        return len(self.docs)

    @traceable(name="search_knowledge_base", run_type="tool")
    async def search(self, query: str, top_k: int = KB_TOP_K) -> str:
        """Search knowledge base using semantic similarity."""
        if not self.docs or not self.embeddings:
            return "Error: Knowledge base not loaded"

        response = await self._client.embeddings.create(
            model=EMBEDDING_MODEL, input=query
        )
        query_embedding = response.data[0].embedding

        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append((i, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = [
            (i, s) for i, s in similarities[:top_k] if s >= KB_RELEVANCE_THRESHOLD
        ]

        if not top_results:
            return "No relevant documents found for this query."

        results = []
        for idx, score in top_results:
            filename, content = self.docs[idx]
            results.append(f"=== {filename} (relevance: {score:.3f}) ===\n{content}\n")

        return "\n".join(results)

    @staticmethod
    def _embeddings_are_stale(kb_path: Path, cache_path: Path) -> bool:
        """Check if any document has been modified after embeddings were generated."""
        if not cache_path.exists():
            return True

        cache_mtime = cache_path.stat().st_mtime
        for file_path in kb_path.glob("*.md"):
            if file_path.name == "CHUNKING_NOTES.md":
                continue
            if file_path.stat().st_mtime > cache_mtime:
                return True
        return False

    async def _generate_and_cache(self, kb_path: Path, cache_path: Path) -> None:
        """Generate embeddings for all documents and save to cache."""
        docs = []
        for file_path in kb_path.glob("*.md"):
            if file_path.name == "CHUNKING_NOTES.md":
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                docs.append((file_path.name, content))

        if not docs:
            return

        self.docs = docs
        self.embeddings = []

        for _filename, content in docs:
            response = await self._client.embeddings.create(
                model=EMBEDDING_MODEL, input=content
            )
            self.embeddings.append(response.data[0].embedding)

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_data = {"docs": docs, "embeddings": self.embeddings}
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)
