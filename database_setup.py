import sqlite3
import os

DATABASE_NAME = 'thesis_database.db'

def setup_database():
    """
    Creates the database and all necessary tables if they don't exist.
    """
    if os.path.exists(DATABASE_NAME):
        print(f"Database '{DATABASE_NAME}' already exists. Setup not needed.")
        return

    print(f"Creating database '{DATABASE_NAME}'...")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # --- Create the 'users' table ---
    print("Creating 'users' table...")
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- Create the 'documents' table ---
    print("Creating 'documents' table...")
    cursor.execute('''
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            storage_path TEXT NOT NULL UNIQUE,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # --- Create the 'messages' table ---
    print("Creating 'messages' table...")
    cursor.execute('''
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            role TEXT NOT NULL, -- 'user' or 'ai'
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database setup complete. All tables created successfully.")

if __name__ == '__main__':
    setup_database()