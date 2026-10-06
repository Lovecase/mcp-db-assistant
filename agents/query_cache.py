import copy
import hashlib
import json
import os
import re
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar

_T = TypeVar("_T")
_RELATIVE_TIME = re.compile(
    r"\b(today|yesterday|tomorrow|this week|last week|past week|this month|"
    r"current month|last month|this quarter|current quarter|last quarter|this year|"
    r"current year|last year|year to date|month to date|(past|last) \d+ (days?|weeks?|months?))\b",
    re.IGNORECASE,
)
_SQL_RELATIVE_TIME = re.compile(
    r"\b(current_date|current_timestamp|current_time)\b|"
    r"\b(date|datetime|strftime)\s*\(\s*['\"]now['\"]",
    re.IGNORECASE,
)


def _positive_int_setting(name: str, default: int) -> int:
    try:
        return max(1, int(os.getenv(name, str(default))))
    except ValueError:
        return default


class InMemoryTTLCache(Generic[_T]):
    def __init__(
        self,
        max_entries: int = 128,
        ttl_seconds: int = 300,
        max_entry_bytes: int = 131072,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_entries < 1 or ttl_seconds < 1 or max_entry_bytes < 1:
            raise ValueError("cache limits must be positive")
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._max_entry_bytes = max_entry_bytes
        self._clock = clock
        self._entries: OrderedDict[str, tuple[float, _T]] = OrderedDict()
        self._lock = threading.RLock()

    def get(self, key: str) -> _T | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at <= self._clock():
                del self._entries[key]
                return None
            self._entries.move_to_end(key)
            return copy.deepcopy(value)

    def set(self, key: str, value: _T) -> None:
        size = len(
            json.dumps(value, default=str, separators=(",", ":")).encode("utf-8")
        )
        if size > self._max_entry_bytes:
            return
        with self._lock:
            self._entries.pop(key, None)
            self._entries[key] = (
                self._clock() + self._ttl_seconds,
                copy.deepcopy(value),
            )
            while len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    def __len__(self) -> int:
        now = self._clock()
        with self._lock:
            expired = [
                key
                for key, (expires_at, _) in self._entries.items()
                if expires_at <= now
            ]
            for key in expired:
                del self._entries[key]
            return len(self._entries)


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_question(question: str) -> str:
    return " ".join(question.casefold().split())


def build_conversation_context(
    history: list[dict[str, Any]],
    question: str,
    max_turns: int = 3,
    max_rows_per_turn: int = 5,
) -> list[dict[str, Any]]:
    if max_turns <= 0:
        return []
    max_rows_per_turn = max(0, max_rows_per_turn)
    turns = [
        turn
        for turn in history
        if turn.get("successful", bool(turn.get("generated_sql")))
    ]
    if turns and normalize_question(
        turns[-1].get("question", "")
    ) == normalize_question(question):
        turns = turns[:-1]

    context = []
    for turn in turns[-max_turns:]:
        context.append(
            {
                "question": turn.get("question", ""),
                "generated_sql": turn.get("generated_sql", ""),
                "columns": turn.get("columns", []),
                "sample_rows": turn.get("sample_rows", [])[:max_rows_per_turn],
                "explanation": turn.get("explanation", ""),
            }
        )
    return context


def schema_fingerprint(schema_context: str) -> str:
    return _digest(schema_context.strip())


def database_revision(database_path: str | Path | None = None) -> str:
    path = (
        Path(database_path)
        if database_path
        else Path(__file__).parent.parent / "data" / "sample.db"
    )
    try:
        stat = path.stat()
    except OSError:
        return f"{path.resolve()}:missing"
    return f"{path.resolve()}:{stat.st_mtime_ns}:{stat.st_size}"


def make_response_cache_key(
    question: str,
    schema_context: str,
    data_revision: str,
    conversation_id: str | None = None,
    conversation_context: list[dict[str, Any]] | None = None,
    authorization_scope: str = "public",
    today: date | None = None,
) -> str | None:
    context = conversation_context or []
    if context and not conversation_id:
        return None

    relative_time = bool(_RELATIVE_TIME.search(question))
    key_data = {
        "question": normalize_question(question),
        "schema": schema_fingerprint(schema_context),
        "data_revision": data_revision,
        "scope": f"conversation:{conversation_id}" if context else authorization_scope,
        "context": _digest(context) if context else None,
        "time_bucket": (today or datetime.now(timezone.utc).date()).isoformat()
        if relative_time
        else None,
    }
    return _digest(key_data)


def make_sql_cache_key(
    sql: str,
    schema_context: str,
    data_revision: str,
    authorization_scope: str = "public",
    today: date | None = None,
) -> str:
    uses_relative_time = bool(_SQL_RELATIVE_TIME.search(sql))
    return _digest(
        {
            "sql": sql.strip(),
            "schema": schema_fingerprint(schema_context),
            "data_revision": data_revision,
            "scope": authorization_scope,
            "time_bucket": (today or datetime.now(timezone.utc).date()).isoformat()
            if uses_relative_time
            else None,
        }
    )


def is_cacheable_response(state: dict[str, Any] | None) -> bool:
    return bool(
        state
        and state.get("sql_error") is None
        and state.get("generated_sql")
        and "query_result" in state
        and isinstance(state.get("explanation"), str)
    )


def invoke_with_response_cache(
    cache: InMemoryTTLCache[dict[str, Any]],
    key: str | None,
    request_state: dict[str, Any],
    invoke: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    if key is not None:
        cached = cache.get(key)
        if cached is not None and is_cacheable_response(cached):
            cached["response_cache_hit"] = True
            return cached

    result = dict(invoke(request_state))
    result["response_cache_hit"] = False
    if key is not None and is_cacheable_response(result):
        cache.set(key, result)
    return result


_DEFAULT_TTL = _positive_int_setting("QUERY_CACHE_TTL_SECONDS", 300)
_DEFAULT_MAX_ENTRIES = _positive_int_setting("QUERY_CACHE_MAX_ENTRIES", 128)
_DEFAULT_MAX_ENTRY_BYTES = _positive_int_setting("QUERY_CACHE_MAX_ENTRY_BYTES", 131072)

response_cache: InMemoryTTLCache[dict[str, Any]] = InMemoryTTLCache(
    max_entries=_DEFAULT_MAX_ENTRIES,
    ttl_seconds=_DEFAULT_TTL,
    max_entry_bytes=_DEFAULT_MAX_ENTRY_BYTES,
)
sql_result_cache: InMemoryTTLCache[dict[str, Any]] = InMemoryTTLCache(
    max_entries=_DEFAULT_MAX_ENTRIES,
    ttl_seconds=_DEFAULT_TTL,
    max_entry_bytes=_DEFAULT_MAX_ENTRY_BYTES,
)
