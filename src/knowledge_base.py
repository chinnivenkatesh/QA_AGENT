import os
from typing import List
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

FAISS_DB_PATH = "faiss_db"
EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

def load_documents(file_paths: List[str]) -> List[Document]:
    docs = []
    for file_path in file_paths:
        _, file_extension = os.path.splitext(file_path)
        loader = None
        try:
            if file_path.endswith('.html') or file_path.endswith('.txt') or file_path.endswith('.json'):
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_extension == '.md':
                loader = UnstructuredMarkdownLoader(file_path)
            
            if loader:
                loaded_docs = loader.load()
                for doc in loaded_docs:
                    doc.metadata["source_document"] = os.path.basename(file_path)
                    docs.append(doc)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return docs

def build_knowledge_base(file_paths: List[str]):
    raw_documents = load_documents(file_paths)
    if not raw_documents: raise ValueError("No documents were loaded.")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(raw_documents)
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_db = FAISS.from_documents(chunks, embeddings)
    vector_db.save_local(FAISS_DB_PATH)
    return vector_db

def get_retriever():
    if not os.path.exists(FAISS_DB_PATH): return None
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return FAISS.load_local(FAISS_DB_PATH, embeddings, allow_dangerous_deserialization=True)

def get_html_content() -> str:
    try:
        with open("uploaded_files/checkout.html", "r", encoding="utf-8") as f: return f.read()
    except: return ""