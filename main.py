from flask import Flask, request, render_template
import os
from werkzeug.utils import secure_filename
from resume_parser import load_all_resumes
from jd_matcher import calculate_similarity
from genai_helper import extract_info_with_gpt

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["RESUME_FOLDER"] = "data/resumes"
app.config["JD_FILE"] = "data/job_description.txt"

# Ensure necessary folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["RESUME_FOLDER"], exist_ok=True)
os.makedirs("data", exist_ok=True)

def get_fit_label(score):
    if score >= 0.70:
        return "Strong"
    elif score >= 0.50:
        return "Moderate"
    else:
        return "Weak"

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    jd_text = ""

    if request.method == "POST":
        # ✅ Clear previous resumes before saving new ones
        for f in os.listdir(app.config["RESUME_FOLDER"]):
            os.remove(os.path.join(app.config["RESUME_FOLDER"], f))

        # Save job description
        jd_text = request.form.get("jd_text", "")
        if jd_text:
            with open(app.config["JD_FILE"], "w", encoding="utf-8") as f:
                f.write(jd_text)

        # Save uploaded resumes
        uploaded_files = request.files.getlist("resumes")
        for file in uploaded_files:
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["RESUME_FOLDER"], filename)
                file.save(filepath)

        # Load JD & Resumes
        with open(app.config["JD_FILE"], "r", encoding="utf-8") as f:
            jd_text = f.read()

        resumes = load_all_resumes(app.config["RESUME_FOLDER"])

        for res in resumes:
            score = float(calculate_similarity(res["text"], jd_text))
            label = get_fit_label(score)
            summary = extract_info_with_gpt(res["text"])

            results.append({
                "filename": res["filename"],
                "score": score,
                "label": label,
                "summary": summary
            })

    return render_template("index.html", results=results, jd_text=jd_text)

if __name__ == "__main__":
    app.run(debug=True)
