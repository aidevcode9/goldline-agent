"""Tests for src/knowledge.py — staleness detection, relevance filtering."""

import json
import tempfile
import time
from pathlib import Path

import pytest

from src.knowledge import KnowledgeBase, MIN_RELEVANCE_THRESHOLD


class TestEmbeddingsAreStale:
    def test_stale_when_no_cache(self, tmp_path):
        kb_path = tmp_path / "documents"
        kb_path.mkdir()
        (kb_path / "test.md").write_text("content")
        cache_path = tmp_path / "embeddings" / "embeddings.json"

        assert KnowledgeBase._embeddings_are_stale(kb_path, cache_path) is True

    def test_not_stale_when_cache_newer(self, tmp_path):
        kb_path = tmp_path / "documents"
        kb_path.mkdir()
        (kb_path / "test.md").write_text("content")

        # Create cache after documents
        time.sleep(0.05)
        cache_path = tmp_path / "embeddings" / "embeddings.json"
        cache_path.parent.mkdir()
        cache_path.write_text("{}")

        assert KnowledgeBase._embeddings_are_stale(kb_path, cache_path) is False

    def test_stale_when_doc_modified(self, tmp_path):
        kb_path = tmp_path / "documents"
        kb_path.mkdir()
        doc = kb_path / "test.md"
        doc.write_text("original")

        cache_path = tmp_path / "embeddings" / "embeddings.json"
        cache_path.parent.mkdir()
        cache_path.write_text("{}")

        # Modify doc after cache
        time.sleep(0.05)
        doc.write_text("modified")

        assert KnowledgeBase._embeddings_are_stale(kb_path, cache_path) is True

    def test_ignores_chunking_notes(self, tmp_path):
        kb_path = tmp_path / "documents"
        kb_path.mkdir()

        cache_path = tmp_path / "embeddings" / "embeddings.json"
        cache_path.parent.mkdir()
        cache_path.write_text("{}")

        # Only CHUNKING_NOTES.md exists and is newer — should not be stale
        time.sleep(0.05)
        (kb_path / "CHUNKING_NOTES.md").write_text("notes")

        assert KnowledgeBase._embeddings_are_stale(kb_path, cache_path) is False


class TestSearchRelevanceThreshold:
    """Test that low-relevance results are filtered out."""

    @pytest.mark.asyncio
    async def test_empty_kb_returns_error(self):
        from unittest.mock import AsyncMock
        kb = KnowledgeBase(AsyncMock())
        result = await kb.search("anything")
        assert "not loaded" in result

    def test_threshold_constant_is_reasonable(self):
        assert 0.1 <= MIN_RELEVANCE_THRESHOLD <= 0.5
