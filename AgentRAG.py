from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import init_chat_model
from langchain_nomic import NomicEmbeddings
from langchain_chroma import Chroma
from langchain import hub
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from langchain.retrievers.multi_query import MultiQueryRetriever
from typing_extensions import List, TypedDict



llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

embeddings = NomicEmbeddings(
    model="nomic-embed-text-v1.5",
    device="gpu",
    inference_mode="local",
    dimensionality=768,
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


def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(
        state["question"],
        k=30,
    )
    # print(retrieved_docs)
    return {"context": retrieved_docs}

# def retrieve(state: State):
#     base_retriever = vector_store.as_retriever(
#         search_kwargs={"k": 9},
#         search_type="similarity",
#         )
#     multi_query_retriever = MultiQueryRetriever.from_llm(
#             retriever=base_retriever, llm=llm
#     )

#     retrieved_docs = multi_query_retriever.invoke(state["question"])
#     return {"context": retrieved_docs}



def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# response = graph.invoke({"question": "Explain Chain of Hindsight to me"})
# response = graph.invoke({"question": "Who looked into LLM-empowered agents for scientific discovery and handling autonomous design?"})
# response = graph.invoke({"question": "Quais são os 6 principios da empresa?"})
# response = graph.invoke({"question": "Qual a politica da empresa em relação a direitos humanos?"})
# response = graph.invoke({"question": "Como eu faço uma solicitação de demanda?"})
# response = graph.invoke({"question": "Qual total de licenças locadas?"})
# response = graph.invoke({"question": "Qual o nomo do Véio do Alho?"})
# response = graph.invoke({"question": "Quem é a mãe de WASHINGTON LUIZ COELHO?"})
# response = graph.invoke({"question": "Qual a data de nascimento de Edevaldo dos Reis?"})
# response = graph.invoke({"question": "Qual a trilha de carreira para alguem trabalhando na área de suporte?"})

# response = graph.invoke({"question": "Quais são as boas práticas de uso do notebook?"})
# response = graph.invoke({"question": "O que eu preciso saber sobre o notebook?"})
# response = graph.invoke({"question": "O que fazer quando identificar um phishing?"})
# response = graph.invoke({"question": "Qual nome do CEO da DGT?"})
response = graph.invoke({"question": "Quais são as 5 verticais da DGT?"})


# Como faço para começar a usar o Gympass?
# Qual nome do CEO da DGT?
# Eu recebo o adiantamento do salário quando eu sair de férias?




print(response["answer"])