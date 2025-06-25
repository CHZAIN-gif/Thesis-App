# Forcing a fresh redeployment to read the secrets file
import streamlit as st
from database_utils import add_user, get_user
from auth import hash_password, verify_password

# --- Page Configuration ---
st.set_page_config(
    page_title="Thesis",
    page_icon="✨",
    layout="wide" # Use the full screen width
)

# --- Session State Initialization ---
# This ensures that the 'username' and 'user_id' keys exist from the start
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

# --- Main App Logic ---

# If the user is not logged in, show the login/signup page
if not st.session_state['username']:
    st.title("Welcome to Thesis 🧠")
    st.subheader("Thesis: Read less, learn more.")
    st.write("---")

    # Arrange Signup and Login forms in two columns
    col1, col2 = st.columns(2)

    with col1:
        # --- SIGNUP FORM ---
        st.subheader("Create a New Account")
        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password", type="password", key="signup_password")
        
        if st.button("Sign Up"):
            if new_username and new_password:
                hashed_pw = hash_password(new_password)
                if add_user(new_username, hashed_pw):
                    st.success("Account created successfully! You can now log in.")
                    st.balloons()
                else:
                    st.error("That username is already taken.")
            else:
                st.warning("Please enter a username and password for signup.")

    with col2:
        # --- LOGIN FORM ---
        st.subheader("Log In to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Log In"):
            if username and password:
                user_data = get_user(username)
                if user_data and verify_password(password, user_data['password_hash']):
                    # If login is successful, store user info in the session state
                    st.session_state['username'] = user_data['username']
                    st.session_state['user_id'] = user_data['id']
                    st.rerun() # Re-run the script to show the logged-in view
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please enter your username and password to log in.")

# If the user IS logged in, show the main dashboard view
else:
    # --- LOGGED-IN VIEW / MAIN DASHBOARD ---
    
    # Display a welcome message and a logout button in the sidebar
    st.sidebar.success(f"Logged in as {st.session_state['username']}")
    if st.sidebar.button("Log Out"):
        # Clear the session state on logout
        for key in st.session_state.keys():
            st.session_state[key] = None
        st.rerun()
    
    # Main page content
    st.title(f"Welcome to your Thesis Dashboard 👋")
    st.info("Please navigate using the sidebar on the left.")
    st.write("---")
    st.header("What is Thesis?")
    st.write("""
    **Thesis** is your personal AI research assistant, designed to help you **read less and learn more**.
    
    **How to get started:**
    1.  Go to the **Upload Document** page to add a PDF to your library.
    2.  The system will analyze your document and create an AI 'memory' for it.
    3.  Go to the **My Documents** page to see your library.
    4.  Click **Chat with this document** to start a conversation and ask questions!
    """)
