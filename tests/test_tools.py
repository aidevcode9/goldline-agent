"""Tests for src/tools.py — SQL safety, stock sanitization, tool dispatch."""

import pytest

from src.tools import (
    _classify_stock,
    _sanitize_results,
    query_database,
    _ALLOWED_SQL_PATTERN,
)


# --- _classify_stock ---


class TestClassifyStock:
    def test_zero_is_out_of_stock(self):
        assert _classify_stock(0) == "out_of_stock"

    def test_negative_is_out_of_stock(self):
        assert _classify_stock(-1) == "out_of_stock"
        assert _classify_stock(-100) == "out_of_stock"

    def test_very_limited_1_to_4(self):
        for qty in [1, 2, 3, 4]:
            assert _classify_stock(qty) == "very_limited"

    def test_limited_5_to_9(self):
        for qty in [5, 6, 7, 8, 9]:
            assert _classify_stock(qty) == "limited"

    def test_low_stock_10_to_20(self):
        for qty in [10, 15, 20]:
            assert _classify_stock(qty) == "low_stock"

    def test_in_stock_above_20(self):
        for qty in [21, 50, 100, 999]:
            assert _classify_stock(qty) == "in_stock"


# --- _sanitize_results ---


class TestSanitizeResults:
    def test_with_column_names_only_sanitizes_quantity(self):
        """When column names are provided, only quantity columns are sanitized."""
        rows = [(1, "Copy Paper", "Paper", 8.99, 45)]
        columns = ["id", "name", "category", "price", "quantity"]
        result = _sanitize_results(rows, columns)
        assert result[0][0] == 1  # id preserved as integer
        assert result[0][3] == 8.99  # price preserved
        assert result[0][4] == "in_stock"  # quantity sanitized

    def test_without_column_names_fallback_sanitizes_all_ints(self):
        """Without column names, all integers are sanitized (conservative)."""
        rows = [(1, "Copy Paper", "Paper", 8.99, 45)]
        result = _sanitize_results(rows)
        assert isinstance(result[0][0], str)  # id also sanitized (fallback)
        assert result[0][3] == 8.99  # price still preserved (float)
        assert isinstance(result[0][4], str)  # quantity sanitized

    def test_zero_quantity_becomes_out_of_stock(self):
        rows = [(3, "Ink", "Toner", 34.99, 0)]
        columns = ["id", "name", "category", "price", "quantity"]
        result = _sanitize_results(rows, columns)
        assert result[0][0] == 3  # id preserved
        assert result[0][4] == "out_of_stock"

    def test_floats_pass_through(self):
        rows = [(1, "Paper", "Paper", 8.99, 10)]
        columns = ["id", "name", "category", "price", "quantity"]
        result = _sanitize_results(rows, columns)
        assert result[0][3] == 8.99

    def test_strings_pass_through(self):
        rows = [("hello", "world")]
        result = _sanitize_results(rows, ["col1", "col2"])
        assert result[0] == ("hello", "world")

    def test_empty_results(self):
        assert _sanitize_results([]) == []

    def test_booleans_not_classified_in_fallback(self):
        rows = [(True, False)]
        result = _sanitize_results(rows)
        assert result[0] == (True, False)

    def test_stock_column_name_variants(self):
        """Columns named 'stock', 'qty', 'inventory', 'count' should be sanitized."""
        rows = [(50, 50, 50, 50)]
        for col_name in ["stock", "qty", "inventory", "count"]:
            columns = ["id", "name", "price", col_name]
            result = _sanitize_results(rows, columns)
            assert result[0][0] == 50  # id preserved
            assert result[0][3] == "in_stock"  # quantity column sanitized


# --- SQL allowlist ---


class TestSQLAllowlist:
    def test_select_allowed(self):
        assert _ALLOWED_SQL_PATTERN.match("SELECT * FROM products")

    def test_select_case_insensitive(self):
        assert _ALLOWED_SQL_PATTERN.match("select name from products")

    def test_pragma_allowed(self):
        assert _ALLOWED_SQL_PATTERN.match("PRAGMA table_info(products)")

    def test_drop_blocked(self):
        assert not _ALLOWED_SQL_PATTERN.match("DROP TABLE products")

    def test_delete_blocked(self):
        assert not _ALLOWED_SQL_PATTERN.match("DELETE FROM products")

    def test_update_blocked(self):
        assert not _ALLOWED_SQL_PATTERN.match("UPDATE products SET price = 0")

    def test_insert_blocked(self):
        assert not _ALLOWED_SQL_PATTERN.match("INSERT INTO products VALUES (1)")

    def test_leading_whitespace_allowed(self):
        assert _ALLOWED_SQL_PATTERN.match("  SELECT * FROM products")

    def test_create_blocked(self):
        assert not _ALLOWED_SQL_PATTERN.match("CREATE TABLE evil (id INT)")


# --- query_database ---


class TestQueryDatabase:
    def test_select_returns_results(self, temp_db):
        result = query_database("SELECT name FROM products WHERE id = 1", temp_db)
        assert "Copy Paper" in result

    def test_preserves_ids_with_column_aware_sanitization(self, temp_db):
        """IDs should not be converted to stock labels when column names are available."""
        result = query_database("SELECT id, name, quantity FROM products WHERE id = 1", temp_db)
        assert "1" in result  # id preserved
        assert "in_stock" in result  # quantity sanitized
        assert "45" not in result  # raw quantity hidden

    def test_blocks_drop(self, temp_db):
        result = query_database("DROP TABLE products", temp_db)
        assert result == "Only SELECT and PRAGMA queries are allowed."

    def test_blocks_delete(self, temp_db):
        result = query_database("DELETE FROM products", temp_db)
        assert result == "Only SELECT and PRAGMA queries are allowed."

    def test_blocks_update(self, temp_db):
        result = query_database("UPDATE products SET price = 0", temp_db)
        assert result == "Only SELECT and PRAGMA queries are allowed."

    def test_sanitizes_quantities(self, temp_db):
        result = query_database("SELECT name, quantity FROM products WHERE id = 1", temp_db)
        assert "45" not in result
        assert "in_stock" in result

    def test_invalid_sql_returns_generic_error(self, temp_db):
        result = query_database("SELECT * FROM nonexistent_table", temp_db)
        assert result == "Database query failed. Please try a different query."
        assert "nonexistent_table" not in result

    def test_pragma_works(self, temp_db):
        result = query_database("PRAGMA table_info(products)", temp_db)
        assert "name" in result

    def test_data_intact_after_blocked_query(self, temp_db):
        """Verify that blocked queries don't affect the database."""
        query_database("DROP TABLE products", temp_db)
        result = query_database("SELECT name FROM products", temp_db)
        assert "Copy Paper" in result
        assert "Database query failed" not in result
