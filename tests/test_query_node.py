import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.query_cache import sql_result_cache
from agents.query_node import _clean_sql, query_node

# ─── _clean_sql ───────────────────────────────────────────────────────────────


def test_clean_sql_strips_sql_fence():
    assert _clean_sql("```sql\nSELECT 1\n```") == "SELECT 1"


def test_clean_sql_strips_plain_fence():
    assert _clean_sql("```\nSELECT * FROM orders\n```") == "SELECT * FROM orders"


def test_clean_sql_passthrough_plain_sql():
    sql = "SELECT id, name FROM customers WHERE region_id = 1"
    assert _clean_sql(sql) == sql


def test_clean_sql_strips_surrounding_whitespace():
    assert _clean_sql("  SELECT 1  ") == "SELECT 1"


def test_clean_sql_multiline_fence():
    raw = "```sql\nSELECT\n  id,\n  name\nFROM orders\n```"
    assert _clean_sql(raw) == "SELECT\n  id,\n  name\nFROM orders"


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def base_state():
    return {
        "user_question": "How many orders are there?",
        "schema_context": "TABLE: orders (1500 rows)\n  - id: INTEGER (PK)",
        "generated_sql": "",
        "query_result": [],
        "sql_error": None,
        "retry_count": 0,
        "explanation": "",
        "should_chart": False,
        "chart_config": None,
    }


@pytest.fixture(autouse=True)
def clear_sql_cache():
    sql_result_cache.clear()


def _mock_llm(sql: str) -> RunnableLambda:
    """Return a LangChain-compatible runnable that always yields the given SQL."""
    return RunnableLambda(lambda _: AIMessage(content=sql))


# ─── query_node — success path ────────────────────────────────────────────────


def test_query_node_increments_retry_count_to_one(base_state):
    mock_result = {"rows": [{"cnt": 1500}], "row_count": 1, "columns": ["cnt"]}
    with (
        patch(
            "agents.query_node._llm", _mock_llm("SELECT COUNT(*) AS cnt FROM orders")
        ),
        patch("agents.query_node._call_tool", return_value=mock_result),
    ):
        result = query_node(base_state)
    assert result["retry_count"] == 1


def test_query_node_success_returns_required_keys(base_state):
    mock_result = {"rows": [{"cnt": 1500}], "row_count": 1, "columns": ["cnt"]}
    with (
        patch(
            "agents.query_node._llm", _mock_llm("SELECT COUNT(*) AS cnt FROM orders")
        ),
        patch("agents.query_node._call_tool", return_value=mock_result),
    ):
        result = query_node(base_state)
    assert "generated_sql" in result
    assert "query_result" in result
    assert "sql_error" in result
    assert "retry_count" in result


def test_query_node_success_sql_error_is_none(base_state):
    mock_result = {"rows": [], "row_count": 0, "columns": []}
    with (
        patch("agents.query_node._llm", _mock_llm("SELECT * FROM orders LIMIT 0")),
        patch("agents.query_node._call_tool", return_value=mock_result),
    ):
        result = query_node(base_state)
    assert result["sql_error"] is None


def test_query_node_success_populates_query_result(base_state):
    rows = [{"region": "North", "total": 5000.0}]
    mock_result = {"rows": rows, "row_count": 1, "columns": ["region", "total"]}
    with (
        patch(
            "agents.query_node._llm",
            _mock_llm("SELECT region, SUM(amount) FROM orders"),
        ),
        patch("agents.query_node._call_tool", return_value=mock_result),
    ):
        result = query_node(base_state)
    assert result["query_result"] == rows


def test_query_node_sql_cache_hit_skips_mcp_execution(base_state):
    mock_result = {"rows": [{"cnt": 1500}], "row_count": 1, "columns": ["cnt"]}
    prompts = []
    mock_llm = RunnableLambda(
        lambda prompt: (
            prompts.append(prompt.to_string())
            or AIMessage(content="SELECT COUNT(*) AS cnt FROM orders")
        )
    )
    with (
        patch("agents.query_node._llm", mock_llm),
        patch("agents.query_node._call_tool", return_value=mock_result) as call_tool,
    ):
        first = query_node(base_state)
        second = query_node(base_state)

    assert first["sql_cache_hit"] is False
    assert second["sql_cache_hit"] is True
    assert second["query_result"] == mock_result["rows"]
    assert call_tool.call_count == 1
    assert len(prompts) == 2


def test_query_node_passes_same_conversation_context_to_sql_prompt(base_state):
    prompts = []
    mock_llm = RunnableLambda(
        lambda prompt: (
            prompts.append(prompt.to_string())
            or AIMessage(
                content="SELECT COUNT(*) AS cnt FROM orders WHERE region_id = 2"
            )
        )
    )
    base_state["conversation_context"] = [
        {
            "question": "Count orders by region",
            "generated_sql": "SELECT region_id, COUNT(*) FROM orders GROUP BY region_id",
            "sample_rows": [{"region_id": 1, "count": 100}],
        }
    ]
    mock_result = {"rows": [{"cnt": 90}], "row_count": 1, "columns": ["cnt"]}

    with (
        patch("agents.query_node._llm", mock_llm),
        patch("agents.query_node._call_tool", return_value=mock_result),
    ):
        query_node(base_state)

    assert "Count orders by region" in prompts[0]
    assert '"region_id": 1' in prompts[0]


def test_query_node_does_not_cache_sql_errors(base_state):
    with (
        patch("agents.query_node._llm", _mock_llm("SELECT * FROM missing_table")),
        patch(
            "agents.query_node._call_tool",
            return_value={"error": "no such table: missing_table"},
        ) as call_tool,
    ):
        first = query_node(base_state)
        second = query_node(base_state)

    assert first["sql_error"] == "no such table: missing_table"
    assert second["sql_error"] == "no such table: missing_table"
    assert call_tool.call_count == 2


def test_query_node_cleans_fenced_sql_before_storing(base_state):
    raw_sql = "SELECT COUNT(*) AS cnt FROM orders"
    fenced = f"```sql\n{raw_sql}\n```"
    mock_result = {"rows": [{"cnt": 1}], "row_count": 1, "columns": ["cnt"]}
    with (
        patch("agents.query_node._llm", _mock_llm(fenced)),
        patch("agents.query_node._call_tool", return_value=mock_result),
    ):
        result = query_node(base_state)
    assert result["generated_sql"] == raw_sql


# ─── query_node — MCP error path ──────────────────────────────────────────────


def test_query_node_mcp_error_sets_sql_error(base_state):
    mock_error = {"error": "no such table: foo"}
    with (
        patch("agents.query_node._llm", _mock_llm("SELECT * FROM foo")),
        patch("agents.query_node._call_tool", return_value=mock_error),
    ):
        result = query_node(base_state)
    assert result["sql_error"] == "no such table: foo"


def test_query_node_mcp_error_omits_query_result(base_state):
    mock_error = {"error": "Only SELECT queries are permitted"}
    with (
        patch("agents.query_node._llm", _mock_llm("DROP TABLE orders")),
        patch("agents.query_node._call_tool", return_value=mock_error),
    ):
        result = query_node(base_state)
    assert "query_result" not in result


def test_query_node_mcp_error_stores_generated_sql(base_state):
    mock_error = {"error": "some error"}
    with (
        patch("agents.query_node._llm", _mock_llm("SELECT * FROM bad_table")),
        patch("agents.query_node._call_tool", return_value=mock_error),
    ):
        result = query_node(base_state)
    assert result["generated_sql"] == "SELECT * FROM bad_table"


# ─── query_node — retry path ──────────────────────────────────────────────────


def test_query_node_retry_increments_from_existing_count(base_state):
    base_state["retry_count"] = 2
    base_state["sql_error"] = "no such table: foo"
    base_state["generated_sql"] = "SELECT * FROM foo"
    mock_result = {"rows": [], "row_count": 0, "columns": []}
    with (
        patch("agents.query_node._llm", _mock_llm("SELECT * FROM orders")),
        patch("agents.query_node._call_tool", return_value=mock_result),
    ):
        result = query_node(base_state)
    assert result["retry_count"] == 3


def test_query_node_retry_clears_sql_error_on_success(base_state):
    base_state["retry_count"] = 1
    base_state["sql_error"] = "previous error"
    base_state["generated_sql"] = "SELECT * FROM foo"
    mock_result = {"rows": [{"id": 1}], "row_count": 1, "columns": ["id"]}
    with (
        patch("agents.query_node._llm", _mock_llm("SELECT id FROM orders LIMIT 1")),
        patch("agents.query_node._call_tool", return_value=mock_result),
    ):
        result = query_node(base_state)
    assert result["sql_error"] is None


def test_query_node_retry_still_fails_sets_new_error(base_state):
    base_state["retry_count"] = 1
    base_state["sql_error"] = "first error"
    base_state["generated_sql"] = "SELECT * FROM foo"
    mock_error = {"error": "second error"}
    with (
        patch("agents.query_node._llm", _mock_llm("SELECT * FROM bar")),
        patch("agents.query_node._call_tool", return_value=mock_error),
    ):
        result = query_node(base_state)
    assert result["sql_error"] == "second error"
    assert result["retry_count"] == 2
