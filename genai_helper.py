import os
import requests
import re
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

def clean_gpt_output(text):
    """Cleans markdown and extra newlines from GPT output."""
    text = re.sub(r"[*#`_~]", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def extract_info_with_gpt(text):
    """Call GPT via OpenRouter to extract summary + skills from resume text."""
    if not api_key:
        return "❌ Missing API key. Check your .env file."

    limited_text = text[:2000].strip() if text else ""

    if not limited_text:
        return "❌ Resume text is empty or invalid."

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
        "model": "deepseek/deepseek-chat",  # You can change model
        "messages": [
            {"role": "system", "content": "You are a resume assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=body,
            timeout=15  # seconds
        )
        response.raise_for_status()
        result = response.json()

        raw_summary = result["choices"][0]["message"]["content"]
        return clean_gpt_output(raw_summary)

    except requests.exceptions.RequestException as e:
        return f"❌ OpenRouter API error: {str(e)}"
    except (KeyError, IndexError):
        return "❌ Unexpected GPT response format."
