
import sqlite3
import json

DB_NAME = "db/knowledge.db"

def init_db():
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print(" SQLite veritabanı başarıyla oluşturuldu.")

def chunk_and_embed_documents(file_path):
    
    print(f" {file_path} işleniyor...")
    

if __name__ == "__main__":
    init_db()
    