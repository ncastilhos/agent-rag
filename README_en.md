# AgentRAG

This project implements a Retrieval-Augmented Generation (RAG) agent using Langchain, ChromaDB, and OpenAI's for the Agent and FastAPI to serve it as a RESTful API.

## Getting Started

Follow these steps to set up and run the project.

### 1. Setup Virtual Environment

**On Windows:**
```bash
py -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Installation

Install the required dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Embed Documents
Before starting the agent, you need to process and embed your documents. You can choose between a cloud-based service or a local model.

#### Using OpenAI (Cloud)
```bash
python LoaderCloud.py
```

#### Using Nomic (Local)
```bash
python LoaderLocal.py
```

### 2. Start the Server

Once the documents are embedded, start the FastAPI server:
```bash
fastapi dev AgentRAGServerOPENAI.py
```
The API will be available at `http://127.0.0.1:8000`.

### 3. Invoke the Agent

Send a `GET` request to the `/AgentInvoke` endpoint with your question.

**Example with `curl`:**
```bash
curl -X GET "http://127.0.0.1:8000/AgentInvoke?prompt=Como%20funciona%20o%20banco%20de%20horas?"
```

**Example with an HTTP client:**
```http
GET http://127.0.0.1:8000/AgentInvoke?prompt=Como funciona o banco de horas?
```