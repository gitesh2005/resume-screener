import os
import fitz  
import docx

def read_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    return text

def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_resume(file_path):
    if file_path.endswith(".pdf"):
        return read_pdf(file_path)
    elif file_path.endswith(".docx"):
        return read_docx(file_path)
    else:
        return ""

def load_all_resumes(folder_path="data/resumes"):
    resume_data = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        content = extract_text_from_resume(file_path)
        resume_data.append({"filename": file_name, "text": content})
    return resume_data
from utils import extract_text  # assume you have this function

def load_resume_from_file(filepath):
    text = extract_text(filepath)
    return {
        "filename": filepath.split("/")[-1],
        "text": text
    }
if __name__ == "__main__":
    data = load_all_resumes()
    for resume in data:
        print("File:", resume["filename"])
        print("Text (first 300 chars):")
        print(resume["text"][:300])
        print("-" * 50)
