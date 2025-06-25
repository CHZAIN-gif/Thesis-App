import streamlit as st
from database_utils import get_single_document
from ai_core import extract_text_from_pdf, generate_insights

st.set_page_config(page_title="Insight Panel", page_icon="🧠")

# --- Function to get and cache insights ---
@st.cache_data(show_spinner="Generating insights...")
def get_insights_for_document(_doc_id):
    document_data = get_single_document(_doc_id)
    if document_data:
        full_text = extract_text_from_pdf(document_data['storage_path'])
        if full_text:
            return generate_insights(full_text)
    return None

# --- Authentication and Document Selection Check ---
if st.session_state.get('username') is None:
    st.error("You need to log in to access this page.")
    st.stop()

if st.session_state.get('selected_doc_id') is None:
    st.error("No document selected.")
    st.info("Please go back to the 'My Documents' page and select 'Get Insights' for a document.")
    st.stop()

# --- Main Page Content ---
doc_id = st.session_state.get('selected_doc_id')
insights = get_insights_for_document(doc_id)

st.title("Insight Panel 🧠")
st.write("Here is an AI-generated analysis of your document.")
st.write("---")

if insights:
    if "error" in insights:
        st.error(f"Could not generate insights: {insights['error']}")
    else:
        # Display One-Sentence Summary
        st.subheader("One-Sentence Summary")
        st.markdown(f"> {insights.get('one_sentence_summary', 'Not available.')}")
        st.write("---")

        # Display Key Concepts
        st.subheader("Key Concepts")
        key_concepts = insights.get('key_concepts', [])
        if key_concepts:
            for concept in key_concepts:
                st.markdown(f"- **{concept}**")
        else:
            st.write("Not available.")
        st.write("---")
        
        # Display Main Arguments
        st.subheader("Main Arguments / Purpose")
        st.write(insights.get('main_arguments', 'Not available.'))

else:
    st.error("There was a problem generating insights for this document.")

