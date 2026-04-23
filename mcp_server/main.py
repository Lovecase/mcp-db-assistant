import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from mcp_server.tools import (
    describe_table,
    execute_query,
    get_sample_data,
    list_tables,
)

app = FastAPI(title="MCP DB Assistant")

_TOOLS = {
    "list_tables":    list_tables,
    "describe_table": describe_table,
    "execute_query":  execute_query,
    "get_sample_data": get_sample_data,
}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/mcp")
@app.post("/mcp/")
async def mcp_handler(request: Request) -> JSONResponse:
    body = await request.json()
    method  = body.get("method", "")
    params  = body.get("params", {})
    req_id  = body.get("id")

    if method != "tools/call":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        })

    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})

    if tool_name not in _TOOLS:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
        })

    try:
        result = await _TOOLS[tool_name](**arguments)
    except Exception as exc:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32000, "message": str(exc)},
        })

    return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": result})


if __name__ == "__main__":
    uvicorn.run("mcp_server.main:app", host="0.0.0.0", port=8000, reload=True)
