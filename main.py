# main.py

from flask import Flask, request, render_template
import os
import tempfile
from werkzeug.utils import secure_filename
# from resume_parser import load_all_resumes # We will remove this import
from jd_matcher import calculate_similarity
from genai_helper import extract_info_with_gpt

# Assuming you will add a new function for parsing individual files in resume_parser.py
from resume_parser import parse_file # NEW IMPORT: Assuming you'll add parse_file to resume_parser.py

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024 # 5MB limit per request (total for all files)
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
            # We no longer need to store all resume_paths, as we process them one by one
            # resume_paths = [] # REMOVE THIS LINE

            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    temp_path = os.path.join(temp_dir, filename)
                    file.save(temp_path)
                    
                    # ⚠️ CRITICAL MEMORY OPTIMIZATION:
                    # Instead of loading ALL resumes into memory with load_all_resumes,
                    # we now parse and process EACH resume individually.
                    # This allows Python's garbage collector to free memory for one resume
                    # before the next one is processed.
                    
                    resume_text = parse_file(temp_path) # Call the new parse_file function

                    # Ensure text was successfully extracted before processing
                    if resume_text:
                        raw_score = calculate_similarity(resume_text, jd_text)
                        score = int(raw_score * 100)
                        label = get_fit_label(score)
                        
                        # Call OpenRouter API for summary
                        summary = extract_info_with_gpt(resume_text)

                        results.append({
                            "filename": filename,
                            "score": score,
                            "label": label,
                            "summary": summary
                        })
                        
                        # Explicitly delete the large text string after use to help garbage collection
                        del resume_text
                    
                    # os.remove(temp_path) # Optional: Remove file immediately after processing if temp_dir cleanup isn't fast enough
                    
        # temp_dir is automatically cleaned up when exiting the 'with' block

    return render_template("index.html", results=results, jd_text=jd_text)

if __name__ == "__main__":
    # IMPORTANT: app.run(debug=True) is for local development only.
    # Render will use Gunicorn to run your app in production, so this block is ignored there.
    # Do NOT run with debug=True in production.
    app.run(debug=True)