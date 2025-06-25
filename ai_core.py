import PyPDF2
import google.generativeai as genai
import streamlit as st
import faiss
import numpy as np
import io

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    pass

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as pdf_file_obj:
            pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
            full_text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        return full_text if full_text.strip() else None
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def split_text_into_chunks(text, chunk_size=1500, chunk_overlap=200):
    if not text: return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

def create_embeddings(text_chunks):
    if not text_chunks:
        return None
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
        with io.BytesIO() as bio:
            faiss.write_index(index, faiss.PyCallbackIOWriter(bio.write))
            return bio.getvalue()
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        return None

def get_chat_response(faiss_index_data, user_question, text_chunks):
    """The main chat function. Now returns the response AND the context for debugging."""
    try:
        index = faiss.read_index(faiss.PyCallbackIOReader(io.BytesIO(faiss_index_data).read))
        question_embedding_result = genai.embed_content(
            model='models/embedding-001',
            content=user_question,
            task_type="retrieval_query"
        )
        question_embedding = question_embedding_result['embedding']
        distances, indices = index.search(np.array([question_embedding]).astype('float32'), k=5)
        
        context = ""
        for i in indices[0]:
            if i >= 0 and i < len(text_chunks):
                context += text_chunks[i] + "\n\n"

        prompt = f"""
        Answer the following user question based ONLY on the provided context. If the answer is not available in the context, clearly say "I could not find the answer in the document."

        CONTEXT:
        {context}

        USER QUESTION:
        {user_question}
        """
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        
        return response.text, context
    except Exception as e:
        # --- THIS IS THE FINAL FIX ---
        # The error handling now also returns two values.
        error_message = f"An error occurred during chat: {e}"
        return error_message, ""
