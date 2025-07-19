# resume_parser.py

import os
import fitz # PyMuPDF
import docx
import gc # Import garbage collection for explicit memory management

# ----------- Resume Readers ------------

def read_pdf(file_path):
    """
    Reads text from a PDF file using PyMuPDF (fitz).
    Includes explicit memory cleanup for pages.
    """
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page_num in range(doc.page_count): # Iterate by page number
                page = doc.load_page(page_num) # Load one page at a time
                text += page.get_text()
                del page # Explicitly delete page object to help release memory
                gc.collect() # Optional: Trigger garbage collection
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def read_docx(file_path):
    """
    Reads text from a DOCX file using python-docx.
    """
    try:
        doc = docx.Document(file_path)
        # Using a generator expression with join is efficient for memory.
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def read_txt(file_path):
    """
    Reads text from a TXT file. Added for completeness if you allow .txt uploads.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""

# ----------- Individual File Parser (MODIFIED for main.py) ------------

# This function is now named 'parse_file' to match the main.py refactoring.
# It handles individual resume files uploaded by the user.
def parse_file(file_path):
    """
    Extracts text from a single resume file based on its extension.
    This function is intended to be called for each individual uploaded file
    in main.py.
    """
    ext = file_path.lower().split(".")[-1]
    if ext == "pdf":
        return read_pdf(file_path)
    elif ext in ["doc", "docx"]: # python-docx handles both, assuming .doc are new XML-based format
        return read_docx(file_path)
    elif ext == "txt":
        return read_txt(file_path)
    else:
        print(f"Unsupported file type: {ext} for {file_path}")
        return ""

# ----------- Loader (REMOVED) ------------

# The 'load_all_resumes' function is REMOVED from this file's core logic
# for the web application's deployment.
# It was previously used for loading a batch of local resumes (e.g., from 'data/resumes').
# In your Flask web app, we are now processing uploaded resumes one by one in main.py,
# which is much more memory efficient.
# If you still need 'load_all_resumes' for an offline script (e.g., for batch training),
# you should keep it in a separate script or your classifier.py, not as part of the
# deployed web app's runtime.

# ----------- Optional: CLI Tester ------------

if __name__ == "__main__":
    # This block now needs to be adjusted since load_all_resumes is removed.
    # You would test parse_file directly with a known local file.
    print("--- Testing parse_file function ---")
    
    # Create a dummy text file for testing
    dummy_txt_path = "test_resume.txt"
    with open(dummy_txt_path, "w") as f:
        f.write("This is a test resume text file.\nIt contains some lines.\nSkills: Python, Data Analysis.")
    
    # Test .txt parsing
    txt_content = parse_file(dummy_txt_path)
    print(f"File: {dummy_txt_path}\nContent (first 100 chars):\n{txt_content[:100]}\n")
    os.remove(dummy_txt_path) # Clean up dummy file

    # Note: For PDF/DOCX testing, you would need actual dummy files.
    # Replace with paths to your local test PDF/DOCX files:
    # test_pdf_path = "path/to/your/test_resume.pdf" 
    # if os.path.exists(test_pdf_path):
    #     pdf_content = parse_file(test_pdf_path)
    #     print(f"File: {test_pdf_path}\nContent (first 100 chars):\n{pdf_content[:100]}\n")
    # else:
    #     print(f"Test PDF not found at {test_pdf_path}. Skipping PDF test.")

    # test_docx_path = "path/to/your/test_resume.docx"
    # if os.path.exists(test_docx_path):
    #     docx_content = parse_file(test_docx_path)
    #     print(f"File: {test_docx_path}\nContent (first 100 chars):\n{docx_content[:100]}\n")
    # else:
    #     print(f"Test DOCX not found at {test_docx_path}. Skipping DOCX test.")

    print("-" * 50)