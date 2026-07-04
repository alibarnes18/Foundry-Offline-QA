import os
from src.db_utils import create_tables, insert_chunk, clear_db, get_chunk_count
from src.llm import get_embedding

DATA_DIR = "data/raw"

def read_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
    
def split_into_chunks(text: str) -> list:
    chunks = text.split("\n\n")
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def ingest_all():

    create_tables()
    clear_db()

    files = [
        f for f in os.listdir(DATA_DIR)
        if f.endswith(".txt") or f.endswith(".md")
    ]

    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)

        print(f"Processing: {filename}")

        text = read_file(filepath)
        chunks = split_into_chunks(text)

        for chunk in chunks:
            embedding = get_embedding(chunk)
            insert_chunk(filename, chunk, embedding)

        print(f"   {len(chunks)} chunks added")  

    print(f"\nTotal chunks in database: {get_chunk_count()}")

if __name__ == "__main__":
    ingest_all()
