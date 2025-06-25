import os
import uuid

# Create a directory to store uploaded files if it doesn't exist
UPLOADS_DIR = "user_uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file):
    """
    Saves an uploaded file to the server with a unique filename.
    Returns the path where the file is stored.
    """
    # Generate a unique filename to prevent overwriting files with the same name
    unique_id = uuid.uuid4().hex
    # Get the file extension (e.g., .pdf)
    file_extension = os.path.splitext(uploaded_file.name)[1]
    # Create the new unique filename
    unique_filename = f"{unique_id}{file_extension}"
    
    # Create the full path to save the file
    save_path = os.path.join(UPLOADS_DIR, unique_filename)
    
    # Write the file's content to the new path
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return save_path