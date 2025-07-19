import os
import fitz  # PyMuPDF
import docx
from PyPDF2 import PdfReader

def read_pdf(file_path):
    try:
        # First try with PyMuPDF
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        if text.strip():
            return text
    except Exception as e:
        print(f"fitz failed for {file_path}: {e}")

    # Fallback: Try PyPDF2
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"PyPDF2 also failed for {file_path}: {e}")
        return ""

def read_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def extract_text_from_resume(file_path):
    ext = file_path.lower().split(".")[-1]
    if ext == "pdf":
        return read_pdf(file_path)
    elif ext == "docx":
        return read_docx(file_path)
    else:
        return ""
