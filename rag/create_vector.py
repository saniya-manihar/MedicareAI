from langchain_community.document_loaders import PyMuPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
load_dotenv()

loader = PyMuPDFLoader("data/medical_knowledge.pdf")
documents = loader.load()
# print(documents.count)
splitter = RecursiveCharacterTextSplitter
(
    chunk_size=500,
    chunk_overlap=50create_vector.py
)

chunks = splitter.split_documents(documents)

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    persist_directory="chroma_db"
)
