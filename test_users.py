# We are importing the functions we created in our other files
from auth import hash_password
from database_utils import add_user

def run_test():
    """
    A simple test to create one user and add them to the database.
    """
    print("--- Running User Creation Test ---")

    # 1. Define a sample username and password
    test_username = "my_first_user"
    test_password = "password123"
    print(f"Attempting to create user: '{test_username}' with password: '{test_password}'")

    # 2. Hash the password using our function from auth.py
    try:
        hashed_pw = hash_password(test_password)
        print("Password hashed successfully!")
    except Exception as e:
        print(f"Error hashing password: {e}")
        return

    # 3. Add the user to the database using our function from database_utils.py
    if add_user(test_username, hashed_pw):
        print("--- Test successful! User should be in the database. ---")
    else:
        print("--- Test failed. User was not added (might already exist). ---")


# This line makes the script runnable
if __name__ == "__main__":
    run_test()