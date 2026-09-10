import sqlite3
import os
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Library-Database-Server")
DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            reader TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            return_date TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM issued_books")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("Кобзар", "Шевченко Т.Г.", "2026-03-01", "2026-03-15"),
            ("Тіні забутих предків", "Коцюбинський М.М.", "2026-03-10", None),
            ("Місто", "Підмогильний В.П.", "2026-03-05", "2026-03-25"),
            ("Захар Беркут", "Франко І.Я.", "2026-03-12", None),
            ("Енеїда", "Котляревський І.П.", "2026-02-20", "2026-03-02"),
        ]
        cursor.executemany(
            "INSERT INTO issued_books (title, reader, issue_date, return_date) VALUES (?, ?, ?, ?)",
            sample_data,
        )
        conn.commit()
    conn.close()

init_db()

@mcp.tool(description="Отримати повний список виданих книг з бази даних")
def get_all_books() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM issued_books")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@mcp.tool(description="Сортувати книги за полем (id, title, reader, issue_date, return_date) та напрямком (ASC, DESC)")
def sort_books(sort_by: str = "id", order: str = "ASC") -> List[Dict[str, Any]]:
    allowed_cols = ["id", "title", "reader", "issue_date", "return_date"]
    col = sort_by if sort_by in allowed_cols else "id"
    direction = "DESC" if order.upper() == "DESC" else "ASC"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM issued_books ORDER BY {col} {direction}")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@mcp.tool(description="Пошук книги в базі даних за назвою або читачем")
def search_books(query: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    param = f"%{query}%"
    cursor.execute("""
        SELECT * FROM issued_books 
        WHERE title LIKE ? OR reader LIKE ?
    """, (param, param))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    mcp.run(transport="stdio")