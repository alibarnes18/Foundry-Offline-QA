import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from foundry_local_sdk import FoundryLocalManager, Configuration

load_dotenv()

azure_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01"
)

EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
LLM_ALIAS = "qwen3-1.7b"

def get_embedding(text: str) -> list[float]:
    response = azure_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding

def get_llm_manager():
    config = Configuration(app_name="foundry-rag")
    manager = FoundryLocalManager(config)
    return manager

def generate_answer(messages: list, manager) -> str:
    model = manager.catalog.get_model(LLM_ALIAS)
    model.download(lambda p: print(f"\rDownloading: {p:.0f}%", end="", flush=True))
    model.load()
    
    client = model.get_chat_client()
    response = client.complete_chat(messages)
    answer = response.choices[0].message.content
    
    if "<think>" in answer and "</think>" in answer:
        answer = answer.split("</think>")[-1].strip()
    
    return answer