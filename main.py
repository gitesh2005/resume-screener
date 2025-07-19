from flask import Flask, request, render_template
import os
import tempfile
from werkzeug.utils import secure_filename
from resume_parser import load_all_resumes
from jd_matcher import calculate_similarity
from genai_helper import extract_info_with_gpt

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB limit
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "doc", "docx", "txt"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def get_fit_label(score):
    if score >= 70:
        return "Strong"
    elif score >= 50:
        return "Moderate"
    else:
        return "Weak"

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    jd_text = ""

    if request.method == "POST":
        jd_text = request.form.get("jd_text", "")
        uploaded_files = request.files.getlist("resumes")

        if not jd_text.strip() or not uploaded_files:
            return render_template("index.html", results=[], jd_text=jd_text, error="Please provide both JD and resumes.")

        with tempfile.TemporaryDirectory() as temp_dir:
            resume_paths = []

            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    temp_path = os.path.join(temp_dir, filename)
                    file.save(temp_path)
                    resume_paths.append(temp_path)

            # Load resumes
            resumes = load_all_resumes(temp_dir)

            for res in resumes:
                raw_score = calculate_similarity(res["text"], jd_text)
                score = int(raw_score * 100)
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
