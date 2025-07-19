# main.py

from flask import Flask, request, render_template
import os
import tempfile
from werkzeug.utils import secure_filename
# We no longer load all resumes at once, so remove the import for load_all_resumes
# from resume_parser import load_all_resumes 
from jd_matcher import calculate_similarity
from genai_helper import extract_info_with_gpt

# IMPORTANT: Import the new parse_file function from resume_parser.py
from resume_parser import parse_file

app = Flask(__name__)
# Set a limit for the total size of all uploaded files per request (e.g., 5MB)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024 
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "doc", "docx", "txt"}

def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def get_fit_label(score):
    """Assigns a 'fit' label based on the similarity score."""
    if score >= 70:
        return "Strong"
    elif score >= 50:
        return "Moderate"
    else:
        return "Weak"

@app.route("/", methods=["GET", "POST"])
def index():
    """Main route for uploading resumes and job descriptions."""
    results = []
    jd_text = ""

    if request.method == "POST":
        jd_text = request.form.get("jd_text", "")
        uploaded_files = request.files.getlist("resumes")

        # Basic input validation
        if not jd_text.strip() or not uploaded_files:
            return render_template("index.html", results=[], jd_text=jd_text, 
                                   error="Please provide both JD text and at least one resume.")

        # Use a temporary directory for uploaded files. It gets cleaned up automatically.
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename) # Sanitize filename for security
                    temp_path = os.path.join(temp_dir, filename)
                    file.save(temp_path) # Save the uploaded file to the temporary directory
                    
                    # ⚠️ CRITICAL MEMORY OPTIMIZATION:
                    # Process each resume individually. This prevents all resume texts
                    # from accumulating in memory, allowing Python's garbage collector
                    # to reclaim memory after each resume is processed.
                    resume_text = parse_file(temp_path) # Parse text from the single file

                    # Ensure text was successfully extracted before proceeding
                    if resume_text:
                        raw_score = calculate_similarity(resume_text, jd_text)
                        score = int(raw_score * 100)
                        label = get_fit_label(score)
                        
                        # Generate summary using the remote LLM
                        summary = extract_info_with_gpt(resume_text)

                        # Store results for display
                        results.append({
                            "filename": filename,
                            "score": score,
                            "label": label,
                            "summary": summary
                        })
                        
                        # Explicitly delete the resume_text string to help garbage collection
                        # and free memory immediately after it's used.
                        del resume_text
                        os.remove(temp_path) # Remove the temp file immediately after processing
                    else:
                        # Handle cases where resume text couldn't be extracted
                        results.append({
                            "filename": filename,
                            "score": 0,
                            "label": "Cannot Process",
                            "summary": "Could not extract text from this file."
                        })
                else:
                    # Handle cases of disallowed file types
                    results.append({
                        "filename": file.filename,
                        "score": 0,
                        "label": "Invalid File",
                        "summary": "Unsupported file type or empty file."
                    })
        # The temporary directory (temp_dir) and its contents are automatically
        # deleted when exiting the 'with tempfile.TemporaryDirectory()' block.

    # Render the HTML template with the results
    return render_template("index.html", results=results, jd_text=jd_text)

if __name__ == "__main__":
    # IMPORTANT: app.run(debug=True) is for local development only.
    # Render will use Gunicorn to run your app in production, so this block will be ignored.
    # Do NOT run with debug=True in production for security and performance reasons.
    print("Running Flask app in development mode.")
    app.run(debug=True, port=os.environ.get("PORT", 5000)) # Use PORT env var if available, else 5000