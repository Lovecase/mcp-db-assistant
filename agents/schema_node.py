import os

import httpx
from dotenv import load_dotenv

from agents.state import AgentState

load_dotenv()

_MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp/")


def _call_tool(name: str, arguments: dict, call_id: int = 1) -> dict:
    response = httpx.post(
        _MCP_URL,
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
            "id": call_id,
        },
    )
    response.raise_for_status()
    return response.json()["result"]


def schema_node(state: AgentState) -> dict:
    if state.get("schema_context"):
        return {}

    tables: list[str] = _call_tool("list_tables", {})["tables"]

    lines: list[str] = []
    for i, table in enumerate(tables):
        desc = _call_tool("describe_table", {"table_name": table}, call_id=i + 2)
        lines.append(f"TABLE: {table} ({desc['row_count']} rows)")
        for col in desc["columns"]:
            pk = " (PK)" if col["pk"] else ""
            lines.append(f"  - {col['name']}: {col['type']}{pk}")
        lines.append("")

    return {"schema_context": "\n".join(lines).strip()}
