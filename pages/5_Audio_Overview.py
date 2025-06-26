import streamlit as st
from database_utils import get_single_document
from ai_core import extract_text_from_pdf, generate_audio_summary
import os

st.set_page_config(page_title="Audio Overview", page_icon="🎧")

@st.cache_data(show_spinner="Generating audio summary... This may take a minute.")
def get_audio_for_document(_doc_id):
    """
    Generates and caches the audio file and its summary text.
    It checks if the files exist first to avoid re-creating them.
    """
    document_data = get_single_document(_doc_id)
    if document_data:
        # Define paths for the audio and its corresponding text summary
        audio_folder = "audio_summaries"
        text_folder = "text_summaries"
        os.makedirs(audio_folder, exist_ok=True)
        os.makedirs(text_folder, exist_ok=True)
        
        audio_path_to_check = os.path.join(audio_folder, f"{_doc_id}.mp3")
        text_path_to_check = os.path.join(text_folder, f"{_doc_id}.txt")

        # Check if the files already exist
        if os.path.exists(audio_path_to_check) and os.path.exists(text_path_to_check):
            with open(text_path_to_check, 'r', encoding='utf-8') as f:
                summary_text = f.read()
            return audio_path_to_check, summary_text

        # If they don't exist, create them
        full_text = extract_text_from_pdf(document_data['storage_path'])
        if full_text:
            audio_path, summary_text = generate_audio_summary(full_text, _doc_id)
            if audio_path and summary_text:
                 with open(text_path_to_check, 'w', encoding='utf-8') as f:
                    f.write(summary_text)
            return audio_path, summary_text
            
    return None, None

# --- Authentication and Document Selection Check ---
if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.stop()

if st.session_state.get('selected_doc_id') is None:
    st.error("No document selected.")
    st.info("Please go back to the 'My Documents' page and select 'Audio Overview' for a document.")
    st.stop()

# --- Main Page Content ---
doc_id = st.session_state.get('selected_doc_id')
audio_file_path, summary_text = get_audio_for_document(doc_id)

st.title("Audio Overview 🎧")
st.write("Listen to an AI-generated summary of your document.")
st.write("---")

if audio_file_path and summary_text:
    st.subheader("Listen to Summary")
    # Display the audio player
    st.audio(audio_file_path, format='audio/mp3')
    
    st.write("---")
    
    st.subheader("Summary Text")
    # Display the summary text that was spoken
    st.markdown(summary_text)
else:
    st.error("There was a problem generating the audio overview for this document. The PDF might be a scan or too complex.")