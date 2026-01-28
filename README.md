# Vanguard Advisor-Assist: Enterprise RAG System

## 🚀 Executive Summary

This is a production-grade **Retrieval-Augmented Generation (RAG)** microservice designed for highly regulated financial environments. It enables Investment Advisors to query internal "Fund Fact Sheets" while enforcing strict **Role-Based Access Control (RBAC)**.

**Key Features:**

- **Security-by-Design:** Implements metadata tagging to prevent "Interns" from accessing "Confidential" documents.
- **Hybrid Cloud Architecture:** "Enterprise Switch" logic supports both Azure OpenAI (Production) and Standard OpenAI (Dev).
- **Microservice API:** Built with **FastAPI** and **Pydantic** for strict type validation and scalability.
- **Modern Tooling:** Uses `uv` for high-speed dependency resolution and lockfile management.

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **LLM Orchestration:** LangChain (v0.3 Core)
- **Vector Database:** ChromaDB (Local/Persistent)
- **API Framework:** FastAPI
- **Dependency Management:** uv

## 🏗️ Architecture

1.  **Ingestion Engine:** PDF pipeline using `pdfplumber` to extract financial tables and tag metadata (`access_level="confidential"`).
2.  **The Brain:** Dynamic RAG chain that injects a `filter` into the Vector Retrieval step based on the user's role.
3.  **API Layer:** Secure REST endpoint (`POST /ask`) that validates input schema before processing.

## ⚡ Quick Start

1.  **Clone & Setup:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/vanguard-rag-bot.git](https://github.com/YOUR_USERNAME/vanguard-rag-bot.git)
    cd vanguard-rag-bot
    uv sync
    ```
2.  **Configure Environment:**
    Create a `.env` file:
    ```ini
    OPENAI_API_KEY="sk-..."
    # AZURE_OPENAI_API_KEY="placeholder" (Optional for Dev Mode)
    ```
3.  **Run Ingestion:**
    ```bash
    uv run src/ingest.py
    ```
4.  **Start API:**
    ```bash
    uv run src/api.py
    ```
