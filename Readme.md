# Foundry Offline QA

A fully offline Q&A assistant built with Microsoft Foundry Local and Azure OpenAI. Ask questions about your documents — answers are generated locally with no internet dependency.

## How it works

1. Documents in `data/raw/` are split into chunks and embedded via Azure OpenAI
2. Embeddings are stored in a local SQLite database
3. When a question is asked, the most relevant chunks are retrieved using cosine similarity
4. Retrieved chunks + question are sent to a local LLM via Foundry Local
5. The answer is returned with source citations

## Tech Stack

| Layer | Technology |
|---|---|
| Local LLM runtime | Microsoft Foundry Local |
| LLM model | Qwen3-1.7b (runs on device) |
| Embeddings | Azure OpenAI text-embedding-3-small |
| Vector store | SQLite |
| UI | Streamlit |
| Language | Python 3.10+ |

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/alibarnes18/Foundry-Offline-QA.git
cd Foundry-Offline-QA

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download models
foundry model download qwen3-1.7b

# 5. Add your .env file
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_KEY=...
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# 6. Add documents to data/raw/ (.txt or .md)

# 7. Run ingestion
python src/ingest.py

# 8. Start the app
streamlit run ui/streamlit_app.py
```

## CLI mode

```bash
python main.py
```

## Project Structure

```
├── data/raw/          # Your documents go here
├── db/                # SQLite database (auto-created)
├── src/
│   ├── db_utils.py    # Database operations
│   ├── ingest.py      # Document chunking and embedding
│   ├── llm.py         # Foundry Local + Azure OpenAI clients
│   ├── prompts.py     # Prompt templates
│   └── retrieval.py   # Cosine similarity search
├── ui/
│   └── streamlit_app.py  # Web interface
└── main.py            # CLI interface
```