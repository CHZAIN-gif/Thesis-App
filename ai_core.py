import PyPDF2
import google.generativeai as genai
import streamlit as st
import faiss
import numpy as np
import os
import time

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("Failed to configure Google AI. Is your API key in .streamlit/secrets.toml correct?")

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as pdf_file_obj:
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text() + "\n"
        return full_text
    except Exception as e:
        return None

def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=100):
    if not text: return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

def create_and_save_embeddings(text_chunks, document_id):
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text_chunks,
            task_type="retrieval_document"
        )
        embeddings = result['embedding']
        dimension = len(embeddings[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings).astype('float32'))
        index_folder = "faiss_indexes"
        os.makedirs(index_folder, exist_ok=True)
        index_path = os.path.join(index_folder, f"{document_id}.index")
        faiss.write_index(index, index_path)
        return index_path
    except Exception as e:
        st.error(f"Could not create AI embeddings. Is your API key valid? Error: {e}")
        return None

def get_chat_response(document_id, user_question, text_chunks):
    """The main chat function."""
    try:
        index_path = f"faiss_indexes/{document_id}.index"
        index = faiss.read_index(index_path)

        question_embedding_result = genai.embed_content(
            model='models/embedding-001',
            content=user_question,
            task_type="retrieval_query"
        )
        question_embedding = question_embedding_result['embedding']
        
        distances, indices = index.search(np.array([question_embedding]).astype('float32'), k=3)
        
        context = ""
        for i in indices[0]:
            if i < len(text_chunks):
                context += text_chunks[i] + "\n"

        # --- NEW DEBUGGING LINES ---
        print("="*50)
        print("CONTEXT PROVIDED TO AI:")
        print(context)
        print("="*50)
        # --- END OF DEBUGGING LINES ---

        prompt = f"""
        You are a helpful AI assistant. Answer the following question based ONLY on the provided context.
        If the answer is not in the context, or if the context is empty, say "I could not find the answer in the document."

        Context:
        {context}

        Question:
        {user_question}
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while getting the chat response: {e}"