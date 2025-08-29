from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain import hub
from langchain_core.documents import Document
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from fastapi import FastAPI
import tiktoken


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


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

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


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    
    #LLM Input Prompt and count
    # print(messages.messages[0].content)
    print("Input token count: " + str(num_tokens_from_string(messages.messages[0].content, "cl100k_base")))

    #LLM Output and count
    response = llm.invoke(messages)
    answer = response.content
    print("Output token count: " + str(num_tokens_from_string(answer, "cl100k_base")))
    print(answer)
    return {"answer": answer}


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


app = FastAPI()

@app.get("/")
async def root():
    return "HHTP Endpoint for AgentRAG DGT"

@app.get("/AgentInvoke")
async def complete_text(prompt: str):
    response = graph.invoke({"question": prompt})
    answer = response["answer"]
    return response["answer"]

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)