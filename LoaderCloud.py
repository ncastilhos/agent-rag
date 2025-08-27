from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
# from langchain_community.document_loaders import WebBaseLoader
# import bs4
from langchain_community.document_loaders import DirectoryLoader
# from langchain_core.vectorstores import InMemoryVectorStore
# from langchain import hub
# from langchain_core.documents import Document
# from langgraph.graph import START, StateGraph
# from typing_extensions import List, TypedDict


embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

vector_store = Chroma(
    collection_name="dgt_rag",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db_gemini",
)

# Load and chunk contents of the blog
# webLoader = WebBaseLoader(
#     web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
#     bs_kwargs=dict(
#         parse_only=bs4.SoupStrainer(
#             class_=("post-content", "post-title", "post-header")
#         )
#     ),
# )
# docs = webLoader.load()

#Folder Load
#Loader_Docs/Código de Ética e Conduta DGT
#Loader_Docs\Departamento TI
#Loader_Docs\Materiais de Marketing\Solicitação de demanda - Marketing\Solicitação de Demanda – MARKETING.docx
#Loader_Docs\xls
loader = DirectoryLoader("Loader_Docs/Departamento TI", glob="**/*.*", show_progress=True, use_multithreading=True)
docs = loader.load()
len(docs)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

# Index chunks
_ = vector_store.add_documents(documents=all_splits)