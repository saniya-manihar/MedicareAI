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

def ask_question(question,profile):

    docs = retriever.invoke(question)
    if not docs:
        return "I couldn't find relevant information in the medical knowledge base."

    

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are an AI Medical Assistant.

Use the patient's profile only if it is relevant to the question.

If the patient's allergy, medical history, age, or blood group affects the answer, mention it.

Do not make assumptions if information is missing.

Answer only from the retrieved medical context.

Answer only from the given context.
Symptoms Identified:
- Mention only symptoms found from the context.

Possible Conditions:
- Mention only conditions supported by the context.

Explanation:
- Explain in simple language.

Health Advice:
- Give general health advice only from the context.

Disclaimer:
- Always consult a healthcare professional.


Patient Profile:
Age: {profile[0] if profile else "Not Provided"}
Gender: {profile[1] if profile else "Not Provided"}
Blood Group: {profile[2] if profile else "Not Provided"}
Allergies: {profile[3] if profile else "Not Provided"}
Medical History: {profile[4] if profile else "Not Provided"}

Context:
{context}

Question:
{question}
Disclaimer:
- Always consult a healthcare professional.
"""

def analyze_prescription(text):

    prompt = f"""
You are an AI Medical Assistant.

Analyze the uploaded document.

If the uploaded document is NOT a medical prescription, reply exactly:

This document does not appear to be a valid medical prescription. Please upload a doctor's prescription.

Otherwise return the answer in this format:

Medicine Name:
-

Purpose:
-

Dosage:
-

Possible Side Effects:
-

Precautions:
-

Prescription Text:
{text}
"""

    response = llm.invoke(prompt)

    return response.content

    response = llm.invoke(prompt)


    return response.content


    