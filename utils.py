# utils.py
from PyPDF2 import PdfReader
import docx

def extract_text(path):
    if path.endswith(".pdf"):
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()

    elif path.endswith(".docx"):
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()

    else:
        raise ValueError("Unsupported file type. Only .pdf and .docx supported.")
