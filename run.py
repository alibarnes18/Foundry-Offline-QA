import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval import get_top_chunks

results = get_top_chunks("What is RAG?", top_k=3)

for i, r in enumerate(results):
    print(f"\n--- Result {i+1} (score: {r['score']:.4f}) ---")
    print(f"Source: {r['source']}")
    print(r['chunk'][:150])