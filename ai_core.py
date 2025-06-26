import pdfplumber
import google.generativeai as genai
import streamlit as st
import faiss
import numpy as np
import io
import json
from gtts import gTTS
import os
from PIL import Image
import pytesseract

# This line might be needed if Tesseract isn't in your system's PATH.
# If you get a "Tesseract not found" error, you would add the full path to your tesseract.exe here.
# For now, we will assume it works automatically since your CMD test was successful.
# pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# --- Configuration ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    pass

# --- CORE FUNCTIONS ---

def extract_text_from_pdf(pdf_path):
    """
    The ultimate text extraction function. It first tries a digital read.
    If that fails, it performs OCR on the pages to "see" the text.
    """
    print(f"Attempting to read document: {pdf_path}")
    full_text = ""
    
    # First, try the fast, digital method using pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=2, layout=True)
                if page_text:
                    full_text += page_text + "\n"
    except Exception as e:
        print(f"Digital extraction with pdfplumber failed: {e}")

    # If digital extraction gives very little text, it might be a scan. Try OCR.
    if len(full_text.strip()) < 200: # If we find less than 200 characters, assume it's a scan
        print("Digital text extraction was poor. Attempting OCR with Tesseract...")
        full_text = "" # Reset text to fill with OCR results
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    print(f"Performing OCR on page {i+1}...")
                    # Convert page to an image
                    im = page.to_image(resolution=300)
                    # Use Tesseract to "see" the text in the image
                    ocr_text = pytesseract.image_to_string(im.original, lang='eng')
                    if ocr_text:
                        full_text += ocr_text + "\n"
        except Exception as e:
            st.error(f"An error occurred during OCR: {e}")
            return None
    
    if full_text.strip():
        print(f"Successfully extracted {len(full_text)} characters.")
        return full_text
    else:
        st.error("Could not extract any text from this PDF. It may be an image-only file or corrupted.")
        return None


# The rest of the functions remain the same as our last successful version
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
    if not text_chunks: return None
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
    except Exception:
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
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        summary_text = response.text
        tts = gTTS(text=summary_text, lang='en')
        audio_folder = "audio_summaries"
        os.makedirs(audio_folder, exist_ok=True)
        audio_path = os.path.join(audio_folder, f"{document_id}.mp3")
        tts.save(audio_path)
        return audio_path, summary_text
    except Exception as e:
        print(f"Error generating audio summary: {e}")
        return None, None