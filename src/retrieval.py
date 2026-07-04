import math
from src.db_utils import get_all_chunks
from src.llm import get_embedding

def cosine_similarity(vec_a: list, vec_b: list) ->  float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))

    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b *b for b in vec_b ))

    if mag_a == 0 or mag_b == 0:
        return 0.0
    
    return dot / (mag_a * mag_b)

def get_top_chunks(query: str, top_k: int = 3) -> list:
    query_embedding = get_embedding(query)

    chunks = get_all_chunks()

    scored_chunks = []

    for chunk in chunks:
        similarity = cosine_similarity(query_embedding, chunk["embedding"])
        scored_chunks.append((similarity, chunk))

    scored_chunks.sort(key = lambda x: x[0], reverse=True) 

    return [
    {**chunk, "score": score}
    for score, chunk in scored_chunks[:top_k]
]
