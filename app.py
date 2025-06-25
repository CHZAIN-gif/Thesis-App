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
# This ensures that the 'username' key exists in the session state from the start
if 'username' not in st.session_state:
    st.session_state['username'] = None

# --- Main Logic: Show Login/Signup or the Main App ---

# If the user is not logged in, show the login/signup page
if not st.session_state['username']:
    st.title("Welcome to Thesis 🧠")
    st.write("Your personal AI research assistant.")
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
                    st.success("Account created successfully!")
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
                    st.session_state['username'] = user_data['username']
                    st.session_state['user_id'] = user_data['id'] # Store user ID as well
                    st.rerun()
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
        st.session_state['username'] = None
        st.session_state['user_id'] = None
        st.rerun()
    
    # Main page content
    st.title(f"Welcome to your Thesis Dashboard 👋")
    st.info("Please navigate to the **Upload Document** page from the sidebar on the left to add your first file.")
    st.write("---")
    st.write("This area will soon be filled with your documents and insights.")