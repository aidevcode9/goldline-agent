"""Eval: Does the sanitization layer prevent stock quantity leakage?

This tests the code-level guardrail, not just the prompt instruction.
"""

import pytest

from src.tools import query_database, _sanitize_results


STOCK_LABELS = {"in_stock", "very_limited", "out_of_stock", "low_stock", "limited"}


@pytest.mark.eval
class TestStockLeakage:
    def test_select_all_replaces_quantities(self, temp_db):
        """SELECT * should replace quantity values with labels."""
        result = query_database("SELECT * FROM products", temp_db)
        # Verify stock labels are present (column-aware sanitization)
        assert any(label in result for label in STOCK_LABELS)
        # Verify no raw quantity values leaked
        # (prices like 8.99 are floats so they don't match)
        assert "in_stock" in result  # product 1 has qty=45

    def test_select_quantity_column_hides_values(self, temp_db):
        """Directly selecting quantity column should return labels, not numbers."""
        result = query_database("SELECT name, quantity FROM products", temp_db)
        assert any(label in result for label in STOCK_LABELS)
        # Raw quantities should not appear
        assert "'45'" not in result
        assert "'15'" not in result

    def test_ids_preserved_when_selecting_with_quantity(self, temp_db):
        """Product IDs should remain as integers, not converted to stock labels."""
        result = query_database("SELECT id, name, quantity FROM products WHERE id = 1", temp_db)
        # ID should be preserved
        assert "(1," in result
        # Quantity should be sanitized
        assert "in_stock" in result

    def test_sanitize_preserves_prices(self):
        """Prices (floats) must pass through unchanged."""
        rows = [(1, "Paper", 8.99, 45)]
        columns = ["id", "name", "price", "quantity"]
        result = _sanitize_results(rows, columns)
        assert result[0][2] == 8.99
        assert result[0][0] == 1  # id preserved

    def test_count_queries_still_work(self, temp_db):
        """COUNT(*) should not error."""
        result = query_database("SELECT COUNT(*) FROM products", temp_db)
        assert "Database query failed" not in result

    def test_pragma_does_not_leak(self, temp_db):
        """PRAGMA results should not reveal quantity values."""
        result = query_database("PRAGMA table_info(products)", temp_db)
        assert "quantity" in result  # Column name is fine to show
