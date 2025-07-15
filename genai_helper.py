import os
import requests
import re
from dotenv import load_dotenv

# ✅ Load .env file
load_dotenv()

# ✅ Fetch key & base_url from .env
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# ✅ Cleanup function to remove Markdown
def clean_gpt_output(text):
    text = re.sub(r"[*#`_~]", "", text)  # remove symbols
    text = re.sub(r"\n{2,}", "\n", text)  # remove extra newlines
    return text.strip()

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
        "HTTP-Referer": "https://giteshresume.ai",  # optional
        "X-Title": "GiteshResumeScreening"
    }

    body = {
        "model": "deepseek/deepseek-chat",  # You can change this
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
        raw_summary = result["choices"][0]["message"]["content"]

        return clean_gpt_output(raw_summary)

    except Exception as e:
        return f"❌ OpenRouter Error: {str(e)}"
