import streamlit as st
from database_utils import add_document
from file_handler import save_uploaded_file
from ai_core import extract_text_from_pdf, extract_text_from_image, split_text_into_chunks, create_embeddings
import time
import os

st.set_page_config(page_title="Upload Document", page_icon="📄")

if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.stop()

st.title("Upload a New Document or Image 📄")
st.write("Upload your PDF or Image files here. The system will use Cloud OCR for scanned documents.")

# Allow multiple file types
uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    file_type = uploaded_file.type
    
    with st.spinner('Saving and processing your file... This may take a moment for large or scanned documents.'):
        try:
            # Save the physical file first
            saved_path = save_uploaded_file(uploaded_file)
            
            text = None
            # Use the correct function based on file type
            if "pdf" in file_type:
                text = extract_text_from_pdf(saved_path)
            elif "image" in file_type:
                # For images, we send the bytes directly to the function
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()
                text = extract_text_from_image(image_bytes, uploaded_file.name)

            if text:
                chunks = split_text_into_chunks(text)
                faiss_index_data = create_embeddings(chunks)
                
                if faiss_index_data:
                    user_id = st.session_state.get('user_id')
                    add_document(user_id, uploaded_file.name, saved_path, faiss_index_data)
                    st.success(f"Successfully processed '{uploaded_file.name}'!")
                    st.info("The document is now ready. Go to the 'My Documents' page to interact with it.")
                else:
                    st.error("Failed to create AI memory for the document.")
            else:
                st.error("Could not extract any text from the file.")

        except Exception as e:
            st.error(f"An error occurred: {e}")