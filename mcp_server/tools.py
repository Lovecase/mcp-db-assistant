from mcp.server.fastmcp import FastMCP

from mcp_server.database import run_query

mcp = FastMCP("db-assistant")


def _get_table_names() -> list[str]:
    rows = run_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    return [row["name"] for row in rows]


def _rows_to_result(rows: list[dict]) -> dict:
    columns = list(rows[0].keys()) if rows else []
    return {"rows": rows, "row_count": len(rows), "columns": columns}


@mcp.tool()
async def list_tables() -> dict:
    return {"tables": _get_table_names()}


@mcp.tool()
async def describe_table(table_name: str) -> dict:
    if table_name not in _get_table_names():
        return {"error": f"Unknown table: {table_name}"}

    try:
        cols  = run_query(f"SELECT * FROM pragma_table_info('{table_name}')")
        count = run_query(f"SELECT COUNT(*) AS cnt FROM {table_name}")
    except ValueError as exc:
        return {"error": str(exc)}

    return {
        "table":    table_name,
        "columns": [
            {"name": c["name"], "type": c["type"], "notnull": c["notnull"], "pk": c["pk"]}
            for c in cols
        ],
        "row_count": count[0]["cnt"],
    }


@mcp.tool()
async def execute_query(sql: str) -> dict:
    try:
        rows = run_query(sql)
    except ValueError as exc:
        return {"error": str(exc)}
    return _rows_to_result(rows)


@mcp.tool()
async def get_sample_data(table_name: str, limit: int = 5) -> dict:
    if table_name not in _get_table_names():
        return {"error": f"Unknown table: {table_name}"}

    try:
        rows = run_query(f"SELECT * FROM {table_name} LIMIT {limit}")
    except ValueError as exc:
        return {"error": str(exc)}
    return _rows_to_result(rows)
