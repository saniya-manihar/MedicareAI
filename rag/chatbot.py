from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
load_dotenv()

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding
)
retriever = vector_db.as_retriever(
    search_kwargs={"k": 2}
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def ask_question(question):

    docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a helpful medical assistant.

Answer only from the given context.

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    return response.content


    