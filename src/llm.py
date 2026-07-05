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
    
    if FoundryLocalManager.instance is not None:
        return FoundryLocalManager.instance
    
    manager = FoundryLocalManager(config)
    return manager

_chat_client = None 

def generate_answer(messages: list, manager) -> str:
    global _chat_client
    
    if _chat_client is None:
        model = manager.catalog.get_model(LLM_ALIAS)
        model.download(lambda p: None)  
        model.load()
        _chat_client = model.get_chat_client()
    
    response = _chat_client.complete_chat(messages)
    answer = response.choices[0].message.content
    
    if "<think>" in answer and "</think>" in answer:
        answer = answer.split("</think>")[-1].strip()
    
    return answer

def generate_answer_cloud(messages: list) -> str:
    response = azure_client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=messages,
        temperature=0.3,
        max_tokens=512
    )
    return response.choices[0].message.content