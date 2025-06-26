import pdfplumber # WE ARE NOW USING THE NEW LIBRARY
import google.generativeai as genai
import streamlit as st
import faiss
import numpy as np
import io
import json
from gtts import gTTS
import os

# --- Configuration ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    pass

# --- CORE FUNCTIONS ---

def extract_text_from_pdf(pdf_path):
    """
    A more robust function to extract text from a PDF using pdfplumber.
    """
    print(f"Attempting to read text from PDF with pdfplumber: {pdf_path}")
    try:
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        print("Text extraction with pdfplumber successful.")
        return full_text if full_text.strip() else None
    except Exception as e:
        print(f"Error reading PDF file with pdfplumber: {e}")
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
        st.error("Cannot create embeddings from empty text.")
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
        st.error(f"Could not create AI embeddings. This might be due to an API issue. Error: {e}")
        return None

def get_chat_response(faiss_index_data, user_question, text_chunks):
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
        return f"An error occurred during chat: {e}", ""

def generate_insights(full_text):
    truncated_text = full_text[:15000]
    prompt = f"""
    Analyze the following document text and provide a structured analysis in JSON format.
    The JSON object should have the following keys:
    - "one_sentence_summary": A single, concise sentence that summarizes the entire document.
    - "key_concepts": A list of 5 to 7 of the most important keywords or concepts found in the text.
    - "main_arguments": A brief summary (2-3 sentences) of the main purpose, arguments, or findings presented in the document.

    Here is the document text:
    ---
    {truncated_text}
    ---
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        insights = json.loads(json_response)
        return insights
    except Exception as e:
        return {"error": str(e)}

def generate_audio_summary(full_text, document_id):
    """Generates a text summary and converts it to an audio file."""
    
    truncated_text = full_text[:15000]
    prompt = f"""
    You are an expert summarizer. Read the following document text and create a concise, easy-to-understand summary of about 200-300 words.
    The summary should be suitable for a short audio overview or podcast segment.
    
    DOCUMENT TEXT:
    ---
    {truncated_text}
    ---
    """
    try:
        # Step 1: Generate the text summary
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        summary_text = response.text

        # Step 2: Convert the summary text to an audio file
        tts = gTTS(text=summary_text, lang='en')
        
        audio_folder = "audio_summaries"
        os.makedirs(audio_folder, exist_ok=True)
        audio_path = os.path.join(audio_folder, f"{document_id}.mp3")
        
        tts.save(audio_path)
        
        return audio_path, summary_text

    except Exception as e:
        print(f"Error generating audio summary: {e}")
        return None, None