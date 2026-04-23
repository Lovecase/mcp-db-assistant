import sqlite3
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Seed the database on first start (file is not committed to the repo)
def _seed_db():
    db_path = ROOT / "data" / "sample.db"
    db_path.parent.mkdir(exist_ok=True)
    if not db_path.exists():
        seed_sql = (ROOT / "data" / "seed.sql").read_text()
        conn = sqlite3.connect(db_path)
        conn.executescript(seed_sql)
        conn.close()

_seed_db()

# Start the MCP/FastAPI server in a daemon thread
import uvicorn
from mcp_server.main import app as fastapi_app

def _run_server():
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="warning")

threading.Thread(target=_run_server, daemon=True).start()
time.sleep(1)

# Hand off to the Streamlit frontend
FRONTEND = ROOT / "frontend" / "app.py"
exec(open(FRONTEND).read(), {**globals(), "__file__": str(FRONTEND)})
