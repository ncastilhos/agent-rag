from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
load_dotenv()
# from langchain_nomic import NomicEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
# from gpt4all import GPT4All
# from langchain_community.llms import GPT4All
# from langchain_community.document_loaders import WebBaseLoader


# embeddings = NomicEmbeddings(
#     model="nomic-embed-text-v1.5",
#     device="gpu",
#     inference_mode="local",
#     dimensionality=768,
# )

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# The vector store is initialized with the new embedding function
vector_store = Chroma(
    collection_name="dgt_rag",
    embedding_function=embeddings,
    persist_directory="./chroma_dgt_rag",
)


# loader = WebBaseLoader(
#     web_paths=[
#         "https://dgt.com.br",
#         "https://dgt.com.br/ouvidoria",
#         "https://dgt.com.br/compare",
#         "https://dgt.com.br/videomonitoramento",
#         "https://dgt.com.br/contato",
#         "https://dgt.com.br/bridgefy",
#         "https://dgt.com.br/smart-school",
#         "https://dgt.com.br/smart-traffic",
#         "https://dgt.com.br/smart-building",
#         "https://dgt.com.br/smart-health",
#         "https://dgt.com.br/smart-enviro",
#         "https://dgt.com.br/smart-places",
#   ]
# )
loader = DirectoryLoader("Docs_md/", glob="**/*.*", show_progress=True, use_multithreading=True)



docs = loader.load()
print(f"Loaded {len(docs)} documents.")

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)
print(f"Created {len(all_splits)} document splits.")

# Index chunks into the vector store
print("Adding documents to the vector store...")
_ = vector_store.add_documents(documents=all_splits)
print("Indexing complete.")