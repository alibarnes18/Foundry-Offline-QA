import sqlite3
import json
import os

DB_PATH = "db/knowledge.db"

def get_connection():
    os.makedirs("db", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():

    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            source    TEXT NOT NULL,
            chunk     TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Tables created successfully")

def insert_chunk(source: str, chunk: str, embedding: list):
    conn = get_connection()
    conn.execute(
        "INSERT INTO documents (source, chunk, embedding) VALUES (?, ?, ?)",
        (source, chunk, json.dumps(embedding)) 
    )
    conn.commit()
    conn.close()

def get_all_chunks() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, source, chunk, embedding FROM documents"
    ).fetchall()
    conn.close()

    return [
        {
            "id":        row[0],
            "source":    row[1],
            "chunk":     row[2],
            "embedding": json.loads(row[3])
        }
        for row in rows
    ]

def clear_db():
    
    conn = get_connection()
    conn.execute("DELETE FROM documents")
    conn.commit()
    conn.close()
    print(" Database cleared.")

def get_chunk_count() -> int:
    
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    conn.close()
    return count


if __name__ == "__main__":
    create_tables()
    
    
    insert_chunk(
        source="test.txt",
        chunk="Bu bir test cümlesidir.",
        embedding=[0.1, 0.2, 0.3]
    )
    
    print(f"Record count: {get_chunk_count()}")  
    
    rows = get_all_chunks()
    print(f"First chunk: {rows[0]['chunk']}")
    print(f"Embedding: {rows[0]['embedding']}")
    
    clear_db()
    print(f"After clearing: {get_chunk_count()}")  