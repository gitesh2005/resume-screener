import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from resume_parser import load_all_resumes
from jd_matcher import calculate_similarity
from genai_helper import extract_info_with_gpt

# Flask app setup
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Score label logic
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

    if request.method == "POST":
        # 1. Get job description from textarea
        jd_text = request.form["jd_text"]

        # 2. Save uploaded resumes
        resume_files = request.files.getlist("resumes")
        for file in resume_files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

        # 3. Process resumes
        resumes = load_all_resumes(app.config["UPLOAD_FOLDER"])

        for res in resumes:
            score = calculate_similarity(res["text"], jd_text)
            label = get_fit_label(score)
            summary = extract_info_with_gpt(res["text"])

            results.append({
                "filename": res["filename"],
                "score": f"{score:.2f}",
                "fit": label,
                "summary": summary
            })

    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
