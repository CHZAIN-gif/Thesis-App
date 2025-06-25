import PyPDF2
import google.generativeai as genai
import streamlit as st
import faiss
import numpy as np
import os
import io # We need to import the io library

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

def create_embeddings(text_chunks):
    """Creates embeddings and returns the FAISS index as binary data."""
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
        
        # --- THIS IS THE NEW, BETTER WAY TO SAVE TO MEMORY ---
        with io.BytesIO() as bio:
            faiss.write_index(index, faiss.PyCallbackIOWriter(bio.write))
            return bio.getvalue()
        
    except Exception as e:
        st.error(f"Could not create AI embeddings: {e}")
        return None

def get_chat_response(faiss_index_data, user_question, text_chunks):
    """The main chat function, now loading the index from binary data."""
    try:
        # --- THIS IS THE NEW, BETTER WAY TO LOAD FROM MEMORY ---
        index = faiss.read_index(faiss.PyCallbackIOReader(io.BytesIO(faiss_index_data).read))

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

        prompt = f"""
        You are a helpful AI assistant. Answer the question based ONLY on the provided context.
        If the answer is not in the context, say "I could not find the answer in the document."

        Context:
        {context}

        Question:
        {user_question}
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during chat: {e}"