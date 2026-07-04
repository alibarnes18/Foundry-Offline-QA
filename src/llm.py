import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from foundry_local_sdk import FoundryLocalManager

load_dotenv()

azure_client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key = os.getenv("AZURE_OPENAI_KEY"),
    api_version = "2024-02-01"
)

EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
LLM_ALIAS = "qwen2.5-0.5b"

def get_embedding(text: str) -> list[float]:
    response = azure_client.embeddings.create(
        model = EMBEDDING_DEPLOYMENT,
        input = text
    )
    return response.data[0].embedding

def get_llm_manager():
    manager = FoundryLocalManager(model_alias=LLM_ALIAS)
    return manager

def generate_answer(messages: list, manager):
    client = manager.get_client()
    model_id = manager.get_mode_info(LLM_ALIAS).id

    response = client.char.completions.create(
        model = model_id,
        messages = messages,
        temperature = 0.3,
        max_tokens = 512
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    
    print("Azure embedding test...")
    vec = get_embedding("What is artificial intelligence?")
    print(f" Vector size: {len(vec)}")  
    print(f"   The first 3 values: {vec[:3]}")

    
    print("\nFoundry Local LLM test...")
    manager = get_llm_manager()
    answer = generate_answer([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Introduce yourself with a single sentence."}
    ], manager)
    print(f"model answer: {answer}")