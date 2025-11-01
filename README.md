# Medical AI Agent System

This repository contains a Medical AI Agent project — built with **Python**, **FastAPI**, **LangGraph** and **Streamlit** UI.

The system consists of **two agents working collaboratively**:

1. **Receptionist Agent**
   - Greets user / asks patient details
   - Routes queries
   - Decides whether enough information is present or not
   - When needed, requests additional context or triggers Clinical Agent

2. **Clinical Agent**
   - Accesses Vector DB (FAISS) for RAG
   - Gives medically-aware responses based on clinical documents
   - Supports deep knowledge queries

These two agents work together to generate a final medical answer.

Environment is managed using **UV**.

---

## Tech Stack

| Component | Usage |
|----------|--------|
| Python | Core Development |
| FastAPI | Backend APIs |
| LangGraph | Multi-agent orchestration |
| Streamlit | Frontend UI |
| FAISS | Vector DB for RAG |
| UV | Environment + dependency manager |

---

## API Endpoints

### 1. `/answer`  (POST)
Used for sending user queries and receiving answers.

Sample:
```json
{
  "query": "headache from last 3 days"
}
```

### 2. `/upload-file` (POST)
Upload PDF / text documents → gets embedded → stored in **FAISS**
Clinical agent uses this vector DB for retrieval.

---

## Project Flow (High-level)

```
User → Streamlit UI → FastAPI → LangGraph
        ↓                 ↓
    Receptionist Agent <—→ Clinical Agent (RAG)
```

---

## Local Setup Guide

### 1) Clone repo
```bash
git clone <this-repo-url>
cd <project-folder>
```

### 2) Create environment with and install libraries with UV
```bash
uv sync
```

### 3) Run FastAPI backend
```bash
uv run uvicorn app:app --reload
```
API docs (Swagger) will be available at:
→ http://localhost:8000/docs

### 4) Run Streamlit UI
```bash
streamlit run ui/client.py
```

---

## Notes

- RAG is powered by FAISS vector DB
- LangGraph nodes internally use interrupt-based logic for multi-turn handling
- Streamlit UI preserves chat history on UI side

---

## Future Scope

- Add Auth / JWT
- Add role selection UI (Doctor / Nurse / Patient)
- Improve medical grounding via additional embeddings / vector stores

---

## License
MIT
