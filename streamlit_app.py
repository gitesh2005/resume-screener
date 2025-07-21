import streamlit as st
import os
import tempfile
import re
from resume_parser import parse_file
from jd_matcher import calculate_similarity
from genai_helper import extract_info_with_gpt

# ✅ Secure filename (Flask-free version)
def secure_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

# ✅ Page setup
st.set_page_config(page_title="AI Resume Screener", layout="wide")
st.title("📄 AI Resume Screener")

# ✅ Job Description input
jd_text = st.text_area("Paste the Job Description (JD) here:", height=200)

# ✅ Resume upload
uploaded_files = st.file_uploader(
    "Upload one or more resumes (PDF, DOCX, or TXT)",
    type=["pdf", "doc", "docx", "txt"],
    accept_multiple_files=True
)

submit = st.button("Analyze Resumes")

# ✅ Main Processing
if submit:
    if not jd_text.strip() or not uploaded_files:
        st.warning("⚠️ Please provide both JD text and at least one resume.")
    else:
        results = []

        with tempfile.TemporaryDirectory() as temp_dir:
            for file in uploaded_files:
                filename = secure_filename(file.name)
                temp_path = os.path.join(temp_dir, filename)
                with open(temp_path, "wb") as f:
                    f.write(file.read())

                resume_text = parse_file(temp_path)

                if resume_text:
                    raw_score = calculate_similarity(resume_text, jd_text)
                    score = int(raw_score * 100)
                    label = "Strong" if score >= 70 else "Moderate" if score >= 50 else "Weak"
                    summary = extract_info_with_gpt(resume_text)
                else:
                    score = 0
                    label = "Cannot Process"
                    summary = "Could not extract text from this file."

                results.append({
                    "filename": filename,
                    "score": score,
                    "label": label,
                    "summary": summary
                })

        # ✅ Display Results
        for res in results:
            st.markdown(f"### 📄 {res['filename']}")
            st.write(f"**Fit Score**: {res['score']}% ({res['label']})")
            st.write("**Summary & Key Skills:**")
            st.success(res['summary'])
