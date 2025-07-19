import os
import fitz  # PyMuPDF
import docx

# ----------- Resume Readers ------------

def read_pdf(file_path):
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
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

# ----------- Loader ------------

def load_all_resumes(folder_path="data/resumes"):
    resume_data = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        if not file_name.lower().endswith((".pdf", ".docx")):
            continue  # skip unsupported files
        
        content = extract_text_from_resume(file_path)
        resume_data.append({
            "filename": file_name,
            "text": content.strip()
        })

    return resume_data

# ----------- Optional: CLI Tester ------------

if __name__ == "__main__":
    data = load_all_resumes()
    for resume in data:
        print("File:", resume["filename"])
        print("Text (first 300 chars):")
        print(resume["text"][:300])
        print("-" * 50)
