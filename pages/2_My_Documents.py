import streamlit as st
from database_utils import get_documents_by_user

st.set_page_config(page_title="My Documents", page_icon="📚")

# --- Authentication Check ---
if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.info("Please go to the main page to log in.")
    st.stop()

# --- Main Page Content ---
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
            
            # When this button is clicked, it just saves the ID and switches pages.
            if st.button("Chat with this document 💬", key=f"chat_{doc['id']}"):
                st.session_state['selected_doc_id'] = doc['id']
                st.switch_page("pages/3_Chat.py")