import json
import os

import httpx
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from agents.query_cache import (
    database_revision,
    make_sql_cache_key,
    sql_result_cache,
)
from agents.state import AgentState

load_dotenv()

_MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp/")

_llm = ChatGroq(model="openai/gpt-oss-20b")

_PROMPT = ChatPromptTemplate.from_template(
    "You are an expert SQL assistant. Given the database schema below and a user question, "
    "write a single valid SQLite SELECT query.\n\n"
    "DATABASE SCHEMA:\n{schema_context}\n\n"
    "USER QUESTION:\n{user_question}\n\n"
    "RECENT CONVERSATION CONTEXT (same conversation only):\n{conversation_context}\n\n"
    "{error_context}"
    "Rules:\n"
    "- Only write SELECT queries. No INSERT, UPDATE, DELETE, DROP.\n"
    "- Use proper SQLite syntax (e.g. strftime for dates).\n"
    "- Use conversation context only to resolve references in the current question.\n"
    "- Always generate a complete query for the current question; do not assume prior results contain all needed rows.\n"
    "- Return ONLY the raw SQL query, no explanation, no markdown, no backticks."
)


def _clean_sql(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner)
    return text.strip()


def _call_tool(name: str, arguments: dict) -> dict:
    response = httpx.post(
        _MCP_URL,
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
            "id": 1,
        },
    )
    response.raise_for_status()
    return response.json()["result"]


def query_node(state: AgentState) -> dict:
    retry_count = state.get("retry_count", 0) + 1

    error_context = ""
    if state.get("sql_error"):
        error_context = (
            f"PREVIOUS ATTEMPT FAILED:\n"
            f"SQL: {state['generated_sql']}\n"
            f"Error: {state['sql_error']}\n"
            f"Please fix the query.\n\n"
        )

    chain = _PROMPT | _llm
    response = chain.invoke(
        {
            "schema_context": state["schema_context"],
            "user_question": state["user_question"],
            "conversation_context": json.dumps(
                state.get("conversation_context", [])[-3:], indent=2, default=str
            ),
            "error_context": error_context,
        }
    )

    sql = _clean_sql(response.content)
    cache_key = make_sql_cache_key(
        sql,
        state["schema_context"],
        database_revision(),
    )
    cached_result = sql_result_cache.get(cache_key)
    if cached_result is not None:
        return {
            "generated_sql": sql,
            "query_result": cached_result["rows"],
            "query_columns": cached_result["columns"],
            "sql_error": None,
            "retry_count": retry_count,
            "sql_cache_hit": True,
        }

    result = _call_tool("execute_query", {"sql": sql})

    if "error" in result:
        return {
            "generated_sql": sql,
            "sql_error": result["error"],
            "retry_count": retry_count,
            "sql_cache_hit": False,
        }

    rows = result["rows"]
    columns = result.get("columns", list(rows[0].keys()) if rows else [])
    sql_result_cache.set(cache_key, {"rows": rows, "columns": columns})

    return {
        "generated_sql": sql,
        "query_result": rows,
        "query_columns": columns,
        "sql_error": None,
        "retry_count": retry_count,
        "sql_cache_hit": False,
    }
