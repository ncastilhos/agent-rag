from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
load_dotenv()
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vector_store = Chroma(
    collection_name="dgt_rag",
    embedding_function=embeddings,
    persist_directory="./chroma_dgt_rag",
)

loader = DirectoryLoader("Docs_md/", glob="**/*.*", show_progress=True, use_multithreading=True)

scrapedLoader = DirectoryLoader("ScrapedData/", glob="**/*.*", show_progress=True, use_multithreading=True)

docs = loader.load()
print(f"Loaded {len(docs)} documents.")

scrapedDocs = scrapedLoader.load()
print(f"Loaded {len(scrapedDocs)} documents.")

allDocs = docs + scrapedDocs

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(allDocs)
print(f"Created {len(all_splits)} document splits.")

# Index chunks into the vector store
print("Adding documents to the vector store...")
_ = vector_store.add_documents(documents=all_splits)
print("Indexing complete.")