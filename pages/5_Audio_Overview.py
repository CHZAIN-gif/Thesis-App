import streamlit as st
from database_utils import get_single_document
from ai_core import extract_text_from_pdf, generate_audio_summary
import os

st.set_page_config(page_title="Audio Overview", page_icon="🎧")

# --- Function to generate the audio ---
# We removed the cache decorator to fix the bug.
def get_audio_for_document(_doc_id):
    document_data = get_single_document(_doc_id)
    if document_data:
        full_text = extract_text_from_pdf(document_data['storage_path'])
        if full_text:
            audio_path, summary_text = generate_audio_summary(full_text, _doc_id)
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

st.title("Audio Overview 🎧")
st.write("Listen to an AI-generated summary of your document.")
st.write("---")

# A button to trigger the generation process
if st.button("Generate Audio Summary Now", type="primary"):
    with st.spinner("Generating audio summary... This may take a minute or two."):
        audio_file_path, summary_text = get_audio_for_document(doc_id)
        
        if audio_file_path and summary_text:
            st.subheader("Listen to Summary")
            st.audio(audio_file_path, format='audio/mp3')
            st.write("---")
            st.subheader("Summary Text")
            st.markdown(summary_text)
        else:
            st.error("There was a problem generating the audio overview for this document. The PDF might be a scan or too complex.")