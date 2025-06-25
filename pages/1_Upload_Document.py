import streamlit as st
from database_utils import add_document
from file_handler import save_uploaded_file
from ai_core import extract_text_from_pdf, split_text_into_chunks, create_and_save_embeddings
import time

st.set_page_config(page_title="Upload Document", page_icon="📄")

if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.info("Please go to the main page to log in.")
else:
    st.title("Upload a New Document 📄")
    st.write("Upload your PDF files here. The system will process it and create its AI 'memory'.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        with st.spinner('Saving and processing your file... This may take a moment.'):
            try:
                # 1. Save the physical file
                saved_path = save_uploaded_file(uploaded_file)
                st.write(f"File saved to: {saved_path}")

                # 2. Record document in the database and get the new ID
                user_id = st.session_state.get('user_id')
                doc_id = add_document(user_id, uploaded_file.name, saved_path)
                
                if doc_id:
                    st.write(f"Document recorded in database with ID: {doc_id}. Now processing for AI...")
                    
                    # 3. Extract text
                    text = extract_text_from_pdf(saved_path)
                    
                    # 4. Split text into chunks
                    chunks = split_text_into_chunks(text)
                    
                    # 5. Create and save embeddings using the new document ID
                    create_and_save_embeddings(chunks, doc_id)
                    
                    st.success(f"Successfully processed '{uploaded_file.name}'!")
                    st.info("The document is now ready for chat. Go to the 'My Documents' page.")
                else:
                    st.error("Could not save document record to the database.")

            except Exception as e:
                st.error(f"An error occurred: {e}")