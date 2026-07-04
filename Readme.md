#  Local RAG Assistant powered by Foundry Local

> A privacy-first, 100% offline Retrieval-Augmented Generation (RAG) assistant built for the Microsoft Summer School 2026.

This repository contains a local Q&A chatbot that retrieves information from a custom document knowledge base without requiring any internet connection. It leverages on-device Large Language Models (LLMs) via Microsoft Foundry Local, utilizing SQLite for vector storage and semantic search.

##  Architecture & Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **LLM Runtime** | `Microsoft Foundry Local` | On-device inference with zero network calls. |
| **Vector Database** | `SQLite` | Lightweight, local storage for document chunks and embeddings. |
| **Backend Logic** | `Python` | Data ingestion, chunking, and similarity search. |
| **Application Type** | `RAG Pipeline` | Semantic search combined with AI generation to reduce hallucinations. |

##  Key Features

* **Absolute Privacy:** 100% offline inference. Your documents and queries never leave your machine.
* **Source-Grounded Answers:** Uses a custom Retrieval-Augmented Generation (RAG) pipeline to ensure answers are backed by local data.
* **Minimalist Design:** Clean, straightforward implementation focused on efficiency and speed.

---
*Developed by Ali Suleymanli — Cybersecurity Learner*