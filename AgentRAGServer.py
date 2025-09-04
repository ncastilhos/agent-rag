#.venv\Scripts\activate
#py -m pip install -r requirements.txt
#fastapi dev AgentRAGServer.py

from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain import hub
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from fastapi import FastAPI
import tiktoken
from typing import Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import uuid
from pydantic import BaseModel

llm = init_chat_model("openai:gpt-4o")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vector_store = Chroma(
    collection_name="dgt_rag",
    embedding_function=embeddings,
    persist_directory="./chroma_dgt_rag",
)

prompt = hub.pull("rlm/rag-prompt")


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    conversation_history: List[BaseMessage]
    session_id: Optional[str]

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(
        state["question"],
        k=3,
    )
    # print("Retrieved docs:")
    # print(retrieved_docs)s

    for document in retrieved_docs:
        print(document.metadata["source"])
    return {"context": retrieved_docs}


def update_memory(state: State):
    """Update conversation history with the current question and prepare for response"""
    # Add the current question to conversation history
    new_history = state.get("conversation_history", []) + [HumanMessage(content=state["question"])]
    return {"conversation_history": new_history}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    
    # Get conversation history
    conversation_history = state.get("conversation_history", [])
    
    # Build conversation context string
    conversation_context = ""
    if len(conversation_history) > 1:
        # Exclude the last human message as it's the current question
        history_messages = conversation_history[:-1]
        conversation_parts = []
        for msg in history_messages:
            # Handle both message objects and dictionaries
            if isinstance(msg, dict):
                msg_type = msg.get("type", "")
                msg_content = msg.get("content", "")
                if msg_type == "HumanMessage":
                    conversation_parts.append(f"Human: {msg_content}")
                elif msg_type == "AIMessage":
                    conversation_parts.append(f"Assistant: {msg_content}")
            elif hasattr(msg, '__class__') and msg.__class__.__name__ == "HumanMessage":
                conversation_parts.append(f"Human: {msg.content}")
            elif hasattr(msg, '__class__') and msg.__class__.__name__ == "AIMessage":
                conversation_parts.append(f"Assistant: {msg.content}")
        
        if conversation_parts:
            conversation_context = "\n\nPrevious conversation:\n" + "\n".join(conversation_parts) + "\n\n"
    
    
    # Create messages with conversation context
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    
    # Modify the system message to include conversation context
    if conversation_context and len(messages.messages) > 0:
        # Add conversation context to the system message
        original_content = messages.messages[0].content
        messages.messages[0].content = conversation_context + original_content
    
    #LLM Input Prompt and count
    # print(messages.messages[0].content)
    print("Input token count: " + str(num_tokens_from_string(messages.messages[0].content, "cl100k_base")))

    #LLM Output and count
    response = llm.invoke(messages)
    answer = response.content
    print("Output token count: " + str(num_tokens_from_string(answer, "cl100k_base")))
    print(answer)
    
    # Add the AI response to conversation history
    updated_history = conversation_history + [AIMessage(content=answer)]
    
    return {"answer": answer, "conversation_history": updated_history}


graph_builder = StateGraph(State)
graph_builder.add_node("update_memory", update_memory)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generate", generate)

# Define the flow: START -> update_memory -> retrieve -> generate
graph_builder.add_edge(START, "update_memory")
graph_builder.add_edge("update_memory", "retrieve")
graph_builder.add_edge("retrieve", "generate")

graph = graph_builder.compile()

# In-memory storage for conversation sessions
conversation_sessions = {}

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    conversation_history: List[dict]

app = FastAPI()

@app.get("/")
async def root():
    return "HTTP Endpoint for AgentRAG DGT with Memory"

@app.post("/AgentInvoke", response_model=ChatResponse)
async def complete_text(request: ChatRequest):
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get or create conversation history for this session
    stored_history = conversation_sessions.get(session_id, [])
    
    # Convert dictionaries back to message objects if needed
    conversation_history = []
    for msg in stored_history:
        if isinstance(msg, dict):
            msg_type = msg.get("type", "")
            msg_content = msg.get("content", "")
            if msg_type == "HumanMessage":
                conversation_history.append(HumanMessage(content=msg_content))
            elif msg_type == "AIMessage":
                conversation_history.append(AIMessage(content=msg_content))
        else:
            conversation_history.append(msg)
    
    # Prepare the state with conversation history
    state = {
        "question": request.question,
        "context": [],
        "answer": "",
        "conversation_history": conversation_history,
        "session_id": session_id
    }
    
    # Run the graph
    response = graph.invoke(state)
    
    # Update the session with the new conversation history
    conversation_sessions[session_id] = response["conversation_history"]
    
    # Convert BaseMessage objects to dictionaries for JSON response
    history_dicts = []
    for msg in response["conversation_history"]:
        history_dicts.append({
            "type": msg.__class__.__name__,
            "content": msg.content
        })
    
    return ChatResponse(
        answer=response["answer"],
        session_id=session_id,
        conversation_history=history_dicts
    )

@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a specific session"""
    if session_id not in conversation_sessions:
        return {"error": "Session not found"}
    
    history_dicts = []
    for msg in conversation_sessions[session_id]:
        history_dicts.append({
            "type": msg.__class__.__name__,
            "content": msg.content
        })
    
    return {
        "session_id": session_id,
        "conversation_history": history_dicts
    }

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a specific session"""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return {"message": f"Conversation {session_id} cleared"}
    return {"error": "Session not found"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)