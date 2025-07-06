from resume_parser import load_all_resumes
from jd_matcher import calculate_similarity

# 1. Load job description
with open("data/job_description.txt", "r", encoding="utf-8") as f:
    jd_text = f.read()

# 2. Load resumes
resumes = load_all_resumes("data/resumes")

from resume_parser import load_all_resumes
from jd_matcher import calculate_similarity

# Load JD
with open("data/job_description.txt", "r", encoding="utf-8") as f:
    jd_text = f.read()

# Load resumes
resumes = load_all_resumes("data/resumes")

# Manual score-based fit logic
def get_fit_label(score):
    if score >= 0.70:
        return "Strong"
    elif score >= 0.50:
        return "Moderate"
    else:
        return "Weak"

# Final Output
for res in resumes:
    score = calculate_similarity(res["text"], jd_text)
    label = get_fit_label(score)
    print(f"File: {res['filename']} → Match Score: {score:.2f} → Fit: {label}")


from genai_helper import extract_info_with_gpt

...

for res in resumes:
    score = calculate_similarity(res["text"], jd_text)
    label = get_fit_label(score)

    print(f"File: {res['filename']} → Match Score: {score:.2f} → Fit: {label}")
    print("🔍 GPT Summary:")
    print(extract_info_with_gpt(res["text"]))
    print("-" * 80)
