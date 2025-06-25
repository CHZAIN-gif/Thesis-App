import streamlit as st
from database_utils import get_messages_by_doc_id, add_message, get_single_document
from ai_core import get_chat_response, extract_text_from_pdf, split_text_into_chunks

st.set_page_config(page_title="Chat with Document", page_icon="💬")

# --- Function to prepare the chat context ---
# This makes sure we always have the latest data
@st.cache_data(show_spinner=False)
def prepare_chat_data(doc_id):
    document_data = get_single_document(doc_id)
    if document_data:
        full_text = extract_text_from_pdf(document_data['storage_path'])
        text_chunks = split_text_into_chunks(full_text)
        return document_data, text_chunks
    return None, None

# --- Authentication and Document Selection Check ---
if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.info("Please go to the main page to log in.")
    st.stop()

if st.session_state.get('selected_doc_id') is None:
    st.error("No document selected.")
    st.info("Please go to the 'My Documents' page and select a document to chat with.")
    st.stop()

# --- If everything is okay, proceed ---
doc_id = st.session_state.get('selected_doc_id')
document_data, text_chunks = prepare_chat_data(doc_id)

if not document_data or not text_chunks:
    st.error("Could not load the document data or its content. Please try re-uploading the file.")
    st.stop()

# --- Main Chat Interface ---
st.title(f"Chat with: *{document_data['original_filename']}* 💬")
st.info("The AI will answer questions based only on the content of this document.")
st.write("---")

# Display previous messages from the database
messages = get_messages_by_doc_id(doc_id)
for msg in messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# Handle new chat input
if prompt := st.chat_input("Ask a question about your document"):
    add_message(doc_id, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("The AI is thinking..."):
            faiss_index_data = document_data['faiss_index']
            response = get_chat_response(faiss_index_data, prompt, text_chunks)
            st.markdown(response)
    
    add_message(doc_id, "assistant", response)