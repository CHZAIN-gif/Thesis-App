from ai_core import extract_text_from_pdf
import os

# --- IMPORTANT: YOU MUST EDIT THE LINE BELOW ---
# Go to your 'user_uploads' folder, right-click on the file inside,
# select 'Copy Path', and paste it between the quotes below.
TEST_PDF_PATH ="E:/Thesis_App/user_uploads/dummy.pdf"


# --- Test Runner ---
def run_pdf_test():
    # First, check if the path you provided is valid
    if not os.path.exists(TEST_PDF_PATH):
        print("="*50)
        print(f"ERROR: The file path '{TEST_PDF_PATH}' is incorrect or does not exist.")
        print("Please edit the 'TEST_PDF_PATH' variable in the test_ai.py file.")
        print("Make sure you have copied the full path.")
        print("="*50)
        return

    print("\n--- Testing PDF Text Extraction ---")
    extracted_text = extract_text_from_pdf(TEST_PDF_PATH)

    if extracted_text:
        print("\n--- TEST SUCCESSFUL ---")
        print(f"Successfully extracted {len(extracted_text)} characters of text.")
        print("\nShowing the first 500 characters:")
        print("---------------------------------")
        print(extracted_text[:500])
        print("---------------------------------")
    else:
        print("\n--- TEST FAILED ---")
        print("Text could not be extracted. Check for errors above.")

if __name__ == "__main__":
    run_pdf_test()