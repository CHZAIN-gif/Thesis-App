import streamlit as st
from database_utils import get_documents_by_user

st.set_page_config(page_title="My Documents", page_icon="📚")

# --- Authentication Check ---
if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
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
            
            # Use three columns for our action buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Chat 💬", key=f"chat_{doc['id']}", use_container_width=True):
                    st.session_state['selected_doc_id'] = doc['id']
                    st.switch_page("pages/3_Chat.py")
            
            with col2:
                if st.button("Get Insights 🧠", key=f"insights_{doc['id']}", use_container_width=True):
                    st.session_state['selected_doc_id'] = doc['id']
                    st.switch_page("pages/4_Insight_Panel.py")
            
            with col3:
                # --- THIS IS OUR NEW BUTTON ---
                if st.button("Audio Overview 🎧", key=f"audio_{doc['id']}", use_container_width=True):
                    st.session_state['selected_doc_id'] = doc['id']
                    # We will create this page in the very next step
                    st.switch_page("pages/5_Audio_Overview.py")
