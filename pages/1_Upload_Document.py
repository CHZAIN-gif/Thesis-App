import streamlit as st
from database_utils import add_document
from file_handler import save_uploaded_file
from ai_core import extract_text_from_pdf, split_text_into_chunks, create_embeddings
import time

st.set_page_config(page_title="Upload Document", page_icon="📄")

# --- Authentication Check ---
if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.info("Please go to the main page to log in.")
else:
    # --- Main Page Content ---
    st.title("Upload a New Document 📄")
    st.write("Upload your PDF files here. The system will process it and create its AI 'memory'.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        with st.spinner('Saving and creating AI memory... This may take a moment.'):
            try:
                # 1. Save the physical file
                saved_path = save_uploaded_file(uploaded_file)
                st.write(f"File saved to: {saved_path}")

                # 2. Extract text from the PDF
                text = extract_text_from_pdf(saved_path)
                if not text:
                    st.error("Could not extract text from the PDF. The file might be empty or a scan.")
                else:
                    st.write("Text extracted. Creating text chunks...")
                    chunks = split_text_into_chunks(text)
                    
                    # 3. Create the AI memory (embeddings)
                    faiss_index_data = create_embeddings(chunks)
                    
                    if faiss_index_data:
                        # 4. Save everything to the database at once
                        user_id = st.session_state.get('user_id')
                        doc_id = add_document(user_id, uploaded_file.name, saved_path, faiss_index_data)
                        st.success(f"Successfully processed '{uploaded_file.name}'!")
                        st.info("The document is now ready for chat. Go to the 'My Documents' page.")
                    else:
                        st.error("Failed to create AI memory for the document.")

            except Exception as e:
                st.error(f"An error occurred: {e}")