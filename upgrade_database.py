import sqlite3
DATABASE_NAME = 'thesis_database.db'

def upgrade():
    print("Connecting to database to add 'faiss_index' column...")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        # Add a new column to the documents table to store the binary FAISS index
        cursor.execute("ALTER TABLE documents ADD COLUMN faiss_index BLOB")
        print("Successfully added 'faiss_index' column to 'documents' table.")
    except sqlite3.OperationalError as e:
        # This error happens if the column already exists, which is okay.
        if "duplicate column name" in str(e):
            print("Column 'faiss_index' already exists. No changes needed.")
        else:
            raise e # Re-raise other operational errors
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    upgrade()