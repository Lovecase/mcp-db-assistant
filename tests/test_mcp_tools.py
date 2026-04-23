import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.tools import (
    describe_table,
    execute_query,
    get_sample_data,
    list_tables,
)

# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def seeded_db(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    seed_sql = (Path(__file__).parent.parent / "data" / "seed.sql").read_text()
    conn = sqlite3.connect(db_path)
    conn.executescript(seed_sql)
    conn.close()
    return db_path


@pytest.fixture(autouse=True)
def patch_db(seeded_db):
    with patch("mcp_server.database._DB_PATH", seeded_db):
        yield


# ─── list_tables ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_tables_returns_all_four():
    result = await list_tables()
    assert set(result["tables"]) == {"orders", "customers", "products", "regions"}


@pytest.mark.asyncio
async def test_list_tables_returns_dict_with_tables_key():
    result = await list_tables()
    assert "tables" in result
    assert isinstance(result["tables"], list)


# ─── describe_table ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_describe_table_orders_row_count():
    result = await describe_table("orders")
    assert result["table"] == "orders"
    assert result["row_count"] == 1500


@pytest.mark.asyncio
async def test_describe_table_columns_shape():
    result = await describe_table("customers")
    col_names = [c["name"] for c in result["columns"]]
    assert "id" in col_names
    assert "name" in col_names
    assert "email" in col_names
    assert "region_id" in col_names
    assert "signup_date" in col_names


@pytest.mark.asyncio
async def test_describe_table_pk_flag():
    result = await describe_table("orders")
    pk_cols = [c["name"] for c in result["columns"] if c["pk"]]
    assert pk_cols == ["id"]


@pytest.mark.asyncio
async def test_describe_table_unknown_returns_error():
    result = await describe_table("nonexistent_table")
    assert "error" in result


# ─── execute_query ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_execute_query_count():
    result = await execute_query("SELECT COUNT(*) AS cnt FROM products")
    assert result["row_count"] == 1
    assert result["rows"][0]["cnt"] == 30


@pytest.mark.asyncio
async def test_execute_query_returns_columns():
    result = await execute_query("SELECT id, name FROM regions")
    assert "columns" in result
    assert set(result["columns"]) == {"id", "name"}


@pytest.mark.asyncio
async def test_execute_query_non_select_returns_error():
    result = await execute_query("DROP TABLE orders")
    assert "error" in result
    assert "SELECT" in result["error"]


@pytest.mark.asyncio
async def test_execute_query_bad_sql_returns_error():
    result = await execute_query("SELECT * FROM table_that_does_not_exist")
    assert "error" in result


# ─── get_sample_data ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_sample_data_default_limit():
    result = await get_sample_data("customers")
    assert result["row_count"] == 5
    assert len(result["rows"]) == 5


@pytest.mark.asyncio
async def test_get_sample_data_custom_limit():
    result = await get_sample_data("products", limit=3)
    assert result["row_count"] == 3
    assert len(result["rows"]) == 3


@pytest.mark.asyncio
async def test_get_sample_data_returns_columns():
    result = await get_sample_data("orders", limit=1)
    assert set(result["columns"]) >= {"id", "customer_id", "product_id", "amount", "status"}


@pytest.mark.asyncio
async def test_get_sample_data_unknown_table_returns_error():
    result = await get_sample_data("nonexistent_table")
    assert "error" in result
