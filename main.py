import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval import get_top_chunks
from src.llm import get_llm_manager, generate_answer
from src.prompts import build_messages

def main():
    print("Starting Foundry Local manager...")
    manager = get_llm_manager()
    print("Ready! Type 'q' to quit.\n" )

    while True:
        question = input("Question: ").strip()

        if question.lower() == "q":
            break

        if not question:
            continue

        chunks = get_top_chunks(question)

        messages = build_messages(chunks, question)

        answer = generate_answer(messages, manager)

        print("\nAnswer:")
        print(answer)

        print("\nSources:")
        for i, chunk in enumerate(chunks,1):
            filename = chunk.get("source", "Unknown")
            text = chunk.get("chunk", "")

            print(f"\n{i}. {filename}")
            print(f"   {text[:150]}...")


if __name__ == "__main__":
    main()