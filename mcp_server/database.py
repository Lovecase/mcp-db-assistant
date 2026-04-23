import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).parent.parent / "data" / "sample.db"


def run_query(sql: str) -> list[dict]:
    first_word = sql.strip().upper().split()[0] if sql.strip() else ""
    if first_word != "SELECT":
        raise ValueError("Only SELECT queries are permitted")

    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(sql)
        rows = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as exc:
        raise ValueError(str(exc)) from exc
    finally:
        conn.close()

    return rows
