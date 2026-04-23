---
title: MCP DB Assistant
emoji: 🗄️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
---

# MCP-Powered Database Assistant

A conversational AI assistant that lets you explore a SQLite database using plain English. Ask a question, get back the generated SQL, a results table, a plain-English explanation, and an optional chart — all powered by a **Model Context Protocol (MCP)** server that keeps the database completely decoupled from the agent logic.

---

## What it does

1. You type a question: *"What is the total revenue by region?"*
2. The LangGraph agent discovers the database schema via MCP
3. An LLM (Llama 3.3 70B via Groq) generates the SQL
4. MCP executes the query safely against SQLite
5. A second LLM call produces a plain-English insight and decides if a chart helps
6. Results, SQL, explanation, and chart appear in the Streamlit UI

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph |
| LLM | Llama 3.3 70B via Groq API (free tier) |
| MCP server | FastAPI + MCP Python SDK |
| Database | SQLite |
| Frontend | Streamlit |
| Charts | Plotly Express |
| Tests | pytest (30 tests — unit + integration) |

---

## Architecture

```
User (Streamlit)
      |
      | plain-English question
      v
 LangGraph Agent
  ├── schema_node    →  MCP: list_tables + describe_table
  ├── query_node     →  Groq LLM generates SQL
  │                  →  MCP: execute_query
  │                  →  retry up to 3x on SQL error
  ├── explanation_node → Groq LLM: plain-English insight + chart decision
  └── error_node     →  friendly message after 3 failed attempts
      |
      v
 MCP Server (FastAPI :8000)
      |
      v
   SQLite DB
```

The MCP layer is the key design decision — agents never touch the database directly. Swapping SQLite for another database only requires changes in `mcp_server/database.py`.

---

## Project structure

```
mcp-db-assistant/
├── mcp_server/
│   ├── database.py        # SQLite connection, SELECT-only guard
│   ├── tools.py           # 4 MCP tools: list_tables, describe_table, execute_query, get_sample_data
│   └── main.py            # FastAPI app, JSON-RPC handler at /mcp
├── agents/
│   ├── state.py           # AgentState TypedDict
│   ├── schema_node.py     # Fetches and caches DB schema via MCP
│   ├── query_node.py      # NL → SQL via LLM, executes via MCP, retries on error
│   ├── explanation_node.py # Results → insight + chart config via LLM
│   ├── error_node.py      # Graceful failure after max retries
│   └── graph.py           # LangGraph StateGraph wiring
├── frontend/
│   └── app.py             # Streamlit UI
├── data/
│   ├── seed.sql           # E-commerce schema + 1500 orders, 200 customers
│   └── sample.db          # Generated — not committed
├── tests/
│   ├── test_mcp_tools.py  # Integration tests for all 4 MCP tools
│   └── test_query_node.py # Unit tests for SQL generation + retry logic
└── requirements.txt
```

---

## Setup

**1. Clone and install dependencies**
```bash
git clone https://github.com/your-username/mcp-db-assistant.git
cd mcp-db-assistant
pip install -r requirements.txt
```

**2. Add your API key**

Create a `.env` file in the project root:
```
GROQ_API_KEY=your-groq-api-key
MCP_SERVER_URL=http://localhost:8000/mcp/
```

Get a free Groq API key at [console.groq.com](https://console.groq.com) — no credit card required.

**3. Seed the database**
```bash
python -c "import sqlite3; conn=sqlite3.connect('data/sample.db'); conn.executescript(open('data/seed.sql').read())"
```

---

## Running

Open two terminals from the project root:

**Terminal 1 — MCP server**
```bash
uvicorn mcp_server.main:app --reload --port 8000
```

**Terminal 2 — Streamlit frontend**
```bash
streamlit run frontend/app.py
```

The app opens at `http://localhost:8501`.

---

## Sample questions

- What is the total revenue by region?
- Which product category generates the most orders?
- Show me monthly revenue trends for the last 12 months
- Who are the top 10 customers by total spend?
- What percentage of orders are refunded?
- What is the average order value for each product category?
- How many new customers signed up each month this year?

---

## Running tests

```bash
python -m pytest tests/ -v
```

```
30 passed in 0.44s
```

Tests run fully offline — no LLM calls, no running server required. The integration tests spin up a temporary in-memory SQLite database seeded from `seed.sql`.

---

## Key design decisions

- **MCP abstraction** — agents use JSON-RPC tool calls over HTTP, never raw SQL connections. The database backend is fully swappable.
- **LangGraph retry loop** — `query_node` retries up to 3 times on SQL errors, passing the previous error back to the LLM to guide the fix.
- **Schema caching** — the schema is fetched once per browser session and reused, cutting MCP calls significantly.
- **SELECT-only guard** — `database.py` rejects any non-SELECT statement before it reaches SQLite.
