import sqlite3

DATABASE_NAME = 'thesis_database.db'

def add_user(username, password_hash):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def add_document(user_id, original_filename, storage_path):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    doc_id = None
    try:
        cursor.execute(
            "INSERT INTO documents (user_id, original_filename, storage_path) VALUES (?, ?, ?)",
            (user_id, original_filename, storage_path)
        )
        doc_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        print(f"Database Error while adding document: {e}")
    finally:
        conn.close()
    return doc_id

def get_documents_by_user(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,))
    documents = cursor.fetchall()
    conn.close()
    return documents

def add_message(document_id, role, content):
    """Saves a new chat message to the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO messages (document_id, role, content) VALUES (?, ?, ?)",
            (document_id, role, content)
        )
        conn.commit()
    except Exception as e:
        print(f"Database Error while adding message: {e}")
    finally:
        conn.close()

def get_messages_by_doc_id(document_id):
    """Fetches all messages for a specific document."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE document_id = ? ORDER BY timestamp ASC", (document_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages