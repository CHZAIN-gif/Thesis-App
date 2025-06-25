import streamlit as st
from database_utils import get_messages_by_doc_id, add_message, get_single_document
from ai_core import get_chat_response, extract_text_from_pdf, split_text_into_chunks

st.set_page_config(page_title="Chat with Document", page_icon="💬")

@st.cache_data(show_spinner="Preparing document...")
def prepare_chat_data(_doc_id):
    document_data = get_single_document(_doc_id)
    if document_data:
        doc_info = dict(document_data)
        full_text = extract_text_from_pdf(doc_info['storage_path'])
        text_chunks = split_text_into_chunks(full_text)
        return doc_info, text_chunks
    return None, None

if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.stop()

if st.session_state.get('selected_doc_id') is None:
    st.error("No document selected.")
    st.stop()

doc_id = st.session_state.get('selected_doc_id')
doc_info, text_chunks = prepare_chat_data(doc_id)

if not doc_info or not text_chunks:
    st.error("Could not load the document data. The PDF might be a scan or empty.")
    st.stop()

st.title(f"Chat with: *{doc_info['original_filename']}* 💬")

# --- NEW DEBUG MODE ---
debug_mode = st.sidebar.checkbox("Show Debug Information")

# Display previous messages
messages = get_messages_by_doc_id(doc_id)
for msg in messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

if prompt := st.chat_input("Ask a question..."):
    add_message(doc_id, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            faiss_index_data = doc_info['faiss_index']
            response, context = get_chat_response(faiss_index_data, prompt, text_chunks)
            st.markdown(response)
    
    add_message(doc_id, "assistant", response)

    if debug_mode:
        with st.expander("DEBUG: Context Provided to AI", expanded=True):
            st.text(context)