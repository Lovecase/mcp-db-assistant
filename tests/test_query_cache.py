from datetime import date

from agents.query_cache import (
    InMemoryTTLCache,
    build_conversation_context,
    invoke_with_response_cache,
    make_response_cache_key,
    make_sql_cache_key,
)


def test_ttl_cache_expires_entries_and_uses_fake_clock():
    now = [0.0]
    cache = InMemoryTTLCache[str](ttl_seconds=5, clock=lambda: now[0])
    cache.set("key", "value")

    assert cache.get("key") == "value"
    now[0] = 5.0
    assert cache.get("key") is None


def test_ttl_cache_evicts_least_recently_used_entry():
    cache = InMemoryTTLCache[str](max_entries=2)
    cache.set("first", "1")
    cache.set("second", "2")
    assert cache.get("first") == "1"
    cache.set("third", "3")

    assert cache.get("first") == "1"
    assert cache.get("second") is None
    assert cache.get("third") == "3"


def test_ttl_cache_returns_defensive_copies():
    cache = InMemoryTTLCache[dict](ttl_seconds=5)
    value = {"rows": [{"count": 1}]}
    cache.set("key", value)

    returned = cache.get("key")
    returned["rows"][0]["count"] = 99

    assert cache.get("key") == {"rows": [{"count": 1}]}


def test_ttl_cache_skips_entries_over_size_limit():
    cache = InMemoryTTLCache[str](max_entry_bytes=5)

    cache.set("large", "too large")

    assert cache.get("large") is None


def test_response_key_scopes_context_and_relative_dates():
    base = make_response_cache_key(
        "How many orders this year?",
        "orders(id)",
        "revision-1",
        today=date(2026, 10, 5),
    )
    next_day = make_response_cache_key(
        "How many orders this year?",
        "orders(id)",
        "revision-1",
        today=date(2026, 10, 6),
    )
    context_a = make_response_cache_key(
        "What about South?",
        "orders(id)",
        "revision-1",
        conversation_id="session-a",
        conversation_context=[{"question": "Revenue by region"}],
    )
    context_b = make_response_cache_key(
        "What about South?",
        "orders(id)",
        "revision-1",
        conversation_id="session-b",
        conversation_context=[{"question": "Revenue by region"}],
    )

    assert base != next_day
    assert context_a != context_b


def test_response_key_reuses_whitespace_normalized_standalone_question():
    first = make_response_cache_key("  Total   revenue? ", "schema", "revision")
    second = make_response_cache_key("total revenue?", "schema", "revision")

    assert first == second


def test_response_key_refuses_context_without_conversation_scope():
    key = make_response_cache_key(
        "What about South?",
        "schema",
        "revision",
        conversation_context=[{"question": "Revenue by region"}],
    )

    assert key is None


def test_conversation_context_is_bounded_and_excludes_immediate_repeat():
    history = [
        {
            "question": f"Question {index}",
            "generated_sql": f"SELECT {index}",
            "columns": ["value"],
            "sample_rows": [{"value": row} for row in range(8)],
            "explanation": f"Explanation {index}",
        }
        for index in range(5)
    ]

    context = build_conversation_context(
        history, " Question 4 ", max_turns=3, max_rows_per_turn=2
    )

    assert [turn["question"] for turn in context] == [
        "Question 1",
        "Question 2",
        "Question 3",
    ]
    assert len(context[0]["sample_rows"]) == 2


def test_conversation_context_ignores_failed_turns():
    context = build_conversation_context(
        [
            {"question": "Failed question", "successful": False},
            {
                "question": "Successful question",
                "successful": True,
                "generated_sql": "SELECT 1",
            },
        ],
        "Follow up",
    )

    assert [turn["question"] for turn in context] == ["Successful question"]


def test_sql_key_changes_when_query_schema_or_database_changes():
    original = make_sql_cache_key("SELECT 1", "schema-a", "revision-a")

    assert make_sql_cache_key("SELECT  1", "schema-a", "revision-a") != original
    assert make_sql_cache_key("SELECT 1", "schema-b", "revision-a") != original
    assert make_sql_cache_key("SELECT 1", "schema-a", "revision-b") != original


def test_sql_relative_time_key_changes_by_utc_day():
    first = make_sql_cache_key(
        "SELECT date('now')", "schema", "revision", today=date(2026, 10, 5)
    )
    next_day = make_sql_cache_key(
        "SELECT date('now')", "schema", "revision", today=date(2026, 10, 6)
    )

    assert first != next_day


def test_response_cache_skips_invocation_on_successful_hit():
    cache = InMemoryTTLCache[dict]()
    calls = []
    request = {"user_question": "Count orders"}
    successful = {
        "generated_sql": "SELECT COUNT(*) FROM orders",
        "query_result": [{"count": 10}],
        "explanation": "There are 10 orders.",
        "sql_error": None,
    }
    invoke = lambda _: calls.append(True) or successful

    first = invoke_with_response_cache(cache, "key", request, invoke)
    second = invoke_with_response_cache(cache, "key", request, invoke)

    assert calls == [True]
    assert first["response_cache_hit"] is False
    assert second["response_cache_hit"] is True


def test_response_cache_does_not_store_failed_results():
    cache = InMemoryTTLCache[dict]()
    failed = {
        "generated_sql": "SELECT * FROM missing",
        "sql_error": "no such table",
        "explanation": "Query failed.",
    }
    calls = []

    invoke_with_response_cache(cache, "key", {}, lambda _: calls.append(1) or failed)
    invoke_with_response_cache(cache, "key", {}, lambda _: calls.append(1) or failed)

    assert calls == [1, 1]


def test_response_cache_stores_empty_successful_results():
    cache = InMemoryTTLCache[dict]()
    calls = []
    successful_empty = {
        "generated_sql": "SELECT id FROM customers WHERE 0",
        "query_result": [],
        "explanation": "No rows matched.",
        "sql_error": None,
    }

    invoke_with_response_cache(
        cache,
        "empty-key",
        {},
        lambda _: calls.append(True) or successful_empty,
    )
    result = invoke_with_response_cache(
        cache,
        "empty-key",
        {},
        lambda _: calls.append(True) or successful_empty,
    )

    assert calls == [True]
    assert result["query_result"] == []
    assert result["response_cache_hit"] is True
