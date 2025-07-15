import os
import requests
import re
from dotenv import load_dotenv

# ✅ Load .env file
load_dotenv()

# ✅ Fetch key & base_url from .env
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# ✅ Convert GPT output into HTML
def convert_to_html(text):
    lines = text.strip().split("\n")
    html_output = ""

    for line in lines:
        line = line.strip()
        if line.startswith("-") or line.startswith("•"):
            content = re.sub(r"^[-•]\s*", "", line)
            html_output += f"<li>{content}</li>\n"
        elif re.match(r"^\d+\.", line):
            html_output += f"<br><strong>{line}</strong><br>\n"
        elif line == "":
            html_output += "<br>"
        else:
            html_output += f"<p>{line}</p>\n"

    # Wrap bullet points in <ul>
    html_output = re.sub(r"((<li>.*?</li>\n)+)", r"<ul>\1</ul>\n", html_output, flags=re.DOTALL)
    return html_output.strip()

# ✅ GPT caller function
def extract_info_with_gpt(text):
    limited_text = text[:2000] if text else "No resume text found."

    prompt = f"""
    From the resume text below, extract:
    1. A bullet-point list of key technical and soft skills
    2. A 2-3 line professional summary

    Resume Text:
    {limited_text}
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://giteshresume.ai",
        "X-Title": "GiteshResumeScreening"
    }

    body = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a resume assistant"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=body
        )
        response.raise_for_status()
        result = response.json()
        raw_output = result["choices"][0]["message"]["content"]

        return convert_to_html(raw_output)

    except Exception as e:
        return f"<p>❌ OpenRouter Error: {str(e)}</p>"
