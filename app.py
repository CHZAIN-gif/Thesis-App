# Forcing a fresh redeployment to read the secrets file
import streamlit as st
from database_utils import add_user, get_user
from auth import hash_password, verify_password

# --- Page Configuration ---
st.set_page_config(
    page_title="Thesis",
    page_icon="✨",
    layout="wide"
)

# --- Session State Initialization ---
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

# --- Main App Logic ---

# If the user is not logged in, show the login/signup page
if not st.session_state['username']:
    
    # --- THIS IS OUR NEW DEBUGGING TEST ---
    st.subheader("Server Status Check:")
    if "GOOGLE_API_KEY" in st.secrets:
        st.success("Secret API Key found by the server!")
    else:
        st.error("SECRET API KEY NOT FOUND BY SERVER.")
    st.write("---")
    # --- END OF DEBUGGING TEST ---

    st.title("Welcome to Thesis 🧠")
    st.subheader("Thesis: Read less, learn more.")

    col1, col2 = st.columns(2)
    # ... (The rest of the login/signup code is exactly the same) ...
    with col1:
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
        st.subheader("Log In to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In"):
            if username and password:
                user_data = get_user(username)
                if user_data and verify_password(password, user_data['password_hash']):
                    st.session_state['username'] = user_data['username']
                    st.session_state['user_id'] = user_data['id']
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please enter your username and password to log in.")

# If the user IS logged in
else:
    st.sidebar.success(f"Logged in as {st.session_state['username']}")
    if st.sidebar.button("Log Out"):
        for key in st.session_state.keys():
            st.session_state[key] = None
        st.rerun()
    
    st.title(f"Welcome to your Thesis Dashboard 👋")
    st.info("Please navigate using the sidebar on the left.")
    # ... (The rest of the welcome message is the same) ...