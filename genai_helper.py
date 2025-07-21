import os
import requests
import re
from dotenv import load_dotenv
import streamlit as st

# ✅ Load environment variables locally (no effect on Streamlit Cloud/Render)
load_dotenv()

# ✅ Get from secrets first, then fallback to env vars
api_key = st.secrets.get("openrouter", {}).get("api_key") or os.getenv("OPENROUTER_API_KEY")
base_url = st.secrets.get("openrouter", {}).get("base_url") or os.getenv("OPENROUTER_BASE_URL")
model_name = "deepseek/deepseek-chat"  # 🔁 You can change this anytime

def clean_gpt_output(text):
    """Cleans markdown and extra newlines from GPT output."""
    text = re.sub(r"[*#`_~]", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def extract_info_with_gpt(text):
    """Calls GPT via OpenRouter to extract skills and summary from resume text."""

    if not api_key or not base_url:
        raise ValueError("❌ API key or base URL not set. Please check Streamlit secrets or .env file.")

    limited_text = text[:2000].strip() if text else ""
    if not limited_text:
        return "❌ Resume text is empty or invalid for summary generation."

    prompt = f"""
From the resume text below, extract:
1. A bullet-point list of key technical and soft skills (limit to 5-7 key skills).
2. A concise 2-3 line professional summary, highlighting main achievements and experience.

Resume Text:
{limited_text}
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://giteshresume.ai",  # Replace with your domain if needed
        "X-Title": "GiteshResumeScreening"
    }

    body = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a helpful and concise resume analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=body,
            timeout=15
        )
        response.raise_for_status()
        result = response.json()
        raw_summary = result["choices"][0]["message"]["content"]
        return clean_gpt_output(raw_summary)

    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API: {e}")
        return f"❌ OpenRouter API error: {str(e)}"
    except (KeyError, IndexError):
        print(f"ERROR: Unexpected GPT response format. Response: {result}")
        return "❌ Unexpected GPT response format."
