import streamlit as st
from database_utils import get_documents_by_user, get_single_document
from ai_core import extract_text_from_pdf, split_text_into_chunks

st.set_page_config(page_title="My Documents", page_icon="📚")

if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.info("Please go to the main page to log in.")
else:
    st.title("My Documents 📚")
    st.write("Here is a list of all the documents you have uploaded.")
    st.write("---")

    user_id = st.session_state.get('user_id')
    user_documents = get_documents_by_user(user_id)

    if not user_documents:
        st.warning("You haven't uploaded any documents yet. Go to the 'Upload Document' page!")
    else:
        for doc in user_documents:
            with st.expander(f"**{doc['original_filename']}** - Uploaded on {doc['uploaded_at'][:10]}"):
                
                # When this button is clicked, it saves the document info and switches pages
                if st.button("Chat with this document 💬", key=f"chat_{doc['id']}"):
                    # Before switching, we need to prepare the context for the chat page
                    full_document_data = get_single_document(doc['id'])
                    full_text = extract_text_from_pdf(full_document_data['storage_path'])
                    text_chunks = split_text_into_chunks(full_text)

                    # Save all necessary info to the session state
                    st.session_state['selected_doc_id'] = full_document_data['id']
                    st.session_state['selected_doc_info'] = dict(full_document_data)
                    st.session_state['text_chunks'] = text_chunks

                    # Switch to the chat page
                    st.switch_page("pages/3_Chat.py")