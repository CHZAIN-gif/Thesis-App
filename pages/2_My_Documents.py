import streamlit as st
from database_utils import get_documents_by_user

st.set_page_config(page_title="My Documents", page_icon="📚")

if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.stop()

st.title("My Documents 📚")
user_id = st.session_state.get('user_id')
user_documents = get_documents_by_user(user_id)

if not user_documents:
    st.warning("You haven't uploaded any documents yet.")
else:
    for doc in user_documents:
        with st.expander(f"**{doc['original_filename']}** - Uploaded on {doc['uploaded_at'][:10]}"):
            if st.button("Chat 💬", key=f"chat_{doc['id']}"):
                st.session_state['selected_doc_id'] = doc['id']
                st.switch_page("pages/3_Chat.py")