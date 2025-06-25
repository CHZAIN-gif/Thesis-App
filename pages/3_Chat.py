import streamlit as st
from database_utils import get_messages_by_doc_id, add_message
from ai_core import get_chat_response

st.set_page_config(page_title="Chat with Document", page_icon="💬")

# --- Authentication Check and State Verification ---
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
doc_info = st.session_state.get('selected_doc_info')
text_chunks = st.session_state.get('text_chunks')

st.title(f"Chat with: *{doc_info['original_filename']}* 💬")
st.info("The AI will answer questions based only on the content of this document.")
st.write("---")

# --- Chat History Display ---
# Load and display previous messages for this document
messages = get_messages_by_doc_id(doc_id)
for msg in messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# --- Chat Input and Logic ---
if prompt := st.chat_input("Ask a question about your document"):
    # Save and display user's message
    add_message(doc_id, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and display AI response
    with st.chat_message("assistant"):
        with st.spinner("The AI is thinking..."):
            # Pass the AI memory (faiss_index) and text chunks to the chat function
            faiss_index_data = doc_info['faiss_index']
            response = get_chat_response(faiss_index_data, prompt, text_chunks)
            st.markdown(response)
    
    # Save AI's message to the database
    add_message(doc_id, "assistant", response)