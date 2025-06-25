import streamlit as st
from database_utils import get_messages_by_doc_id, add_message
from ai_core import get_chat_response, extract_text_from_pdf, split_text_into_chunks

st.set_page_config(page_title="Chat with Document", page_icon="💬")

# --- Authentication Check and State Verification ---
if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.info("Please go to the main page to log in.")
elif st.session_state.get('selected_doc_id') is None:
    st.error("No document selected.")
    st.info("Please go to the 'My Documents' page and select a document to chat with.")
else:
    doc_id = st.session_state.get('selected_doc_id')
    doc_path = st.session_state.get('selected_doc_path')

    st.title(f"Chat with your Document 💬")
    st.info(f"You are now chatting with the document stored at: `{doc_path}`")
    st.write("---")

    # Load and display previous messages
    messages = get_messages_by_doc_id(doc_id)
    for msg in messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

    # --- Chat Input and Logic ---
    if prompt := st.chat_input("Ask a question about your document"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to database
        add_message(doc_id, "user", prompt)

        # Get and display AI response
        with st.chat_message("assistant"):
            with st.spinner("The AI is thinking..."):
                # We need the text chunks for context
                full_text = extract_text_from_pdf(doc_path)
                chunks = split_text_into_chunks(full_text)
                
                response = get_chat_response(doc_id, prompt, chunks)
                st.markdown(response)
        
        # Add AI response to database
        add_message(doc_id, "assistant", response)