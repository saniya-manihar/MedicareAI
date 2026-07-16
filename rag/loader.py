from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma  import Chroma
from langchain_ollama import ChatOllama

loader=PyMuPDFLoader("data/medical_knowledge.pdf")
documents=loader.load()
splitter=RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_db=Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    persist_directory="chroma_db",
      



)
llm = ChatOllama(
    model="llama3.2"
)
retriever=vector_db.as_retriever(
search_kwargs={"k": 2}
)
question = "What are the symptoms of diabetes?"
result =retriever.invoke(question)


    

response = llm.invoke("What are the symptoms of diabetes?")

print(response.content)