# genai_helper.py

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
        # It's better to raise an exception in production if API key is missing
        # so deployment fails clearly, rather than returning an error string.
        # For development, the string is fine.
        raise ValueError("❌ Missing OPENROUTER_API_KEY. Set it in your Render environment variables.")

    # Truncate input text to manage token costs and API limits.
    # 2000 characters is a good starting point; you can adjust based on resume length and desired detail.
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
        "HTTP-Referer": "https://giteshresume.ai", # Replace with your actual domain for OpenRouter tracking
        "X-Title": "GiteshResumeScreening" # Replace with your project title
    }

    body = {
        "model": "deepseek/deepseek-chat", # You can change model if you prefer another on OpenRouter
        "messages": [
            {"role": "system", "content": "You are a resume assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        # Reducing max_tokens can save cost and may slightly reduce the response object's memory footprint
        # if the default LLM output is very verbose. For 2-3 lines, 200-300 tokens might be enough.
        "max_tokens": 500 # Adjusted from 1000, can go lower if 2-3 lines is strict.
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=body,
            timeout=15 # seconds - Ensure this is enough for API call latency
        )
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        raw_summary = result["choices"][0]["message"]["content"]
        return clean_gpt_output(raw_summary)

    except requests.exceptions.RequestException as e:
        # Log the full exception for debugging in production, but return a friendly message
        print(f"Error calling OpenRouter API: {e}")
        return f"❌ OpenRouter API error: {str(e)}"
    except (KeyError, IndexError):
        print(f"ERROR: Unexpected GPT response format. Response: {result}")
        return "❌ Unexpected GPT response format."