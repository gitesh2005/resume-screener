# genai_helper.py

import os
import requests
import re
from dotenv import load_dotenv

# ✅ Load environment variables from a .env file locally.
# On Render, environment variables are set directly in the dashboard,
# so this line will have no effect but is harmless.
load_dotenv()

# Retrieve API key and base URL from environment variables.
# This is crucial for security - NEVER hardcode your API key.
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

def clean_gpt_output(text):
    """Cleans markdown and extra newlines from GPT output."""
    # Remove common markdown characters
    text = re.sub(r"[*#`_~]", "", text)
    # Reduce multiple newlines to single newlines
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def extract_info_with_gpt(text):
    """
    Calls GPT via OpenRouter to extract a professional summary and skills from resume text.
    """
    if not api_key:
        # In a production environment, it's often better to raise an exception
        # if a critical API key is missing, so deployment fails clearly.
        # For development/testing, you might return an error string.
        raise ValueError("❌ OPENROUTER_API_KEY environment variable not set. Please configure it on Render.")

    # Truncate the input text to manage token costs and API limits.
    # 2000 characters is a good starting point; adjust based on average resume length
    # and the desired detail for the summary.
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
        # IMPORTANT: Replace with your actual domain for OpenRouter tracking/compliance
        "HTTP-Referer": "https://giteshresume.ai",
        # IMPORTANT: Replace with your project title
        "X-Title": "GiteshResumeScreening"
    }

    body = {
        # You can change this model to another one available on OpenRouter if desired.
        # 'deepseek/deepseek-chat' is a good, performant, and often cost-effective choice.
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful and concise resume analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7, # Controls creativity; 0.7 is a good balance
        # Limiting max_tokens can save cost and reduce response payload size.
        # For a 2-3 line summary + bullet points, 200-300 tokens might be sufficient.
        "max_tokens": 500 # Adjusted from 1000 for efficiency
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=body,
            timeout=15 # seconds - Set a reasonable timeout for the API call
        )
        response.raise_for_status() # Raises an HTTPError for 4xx/5xx responses
        result = response.json()

        raw_summary = result["choices"][0]["message"]["content"]
        return clean_gpt_output(raw_summary)

    except requests.exceptions.RequestException as e:
        # Log the full exception for debugging in production, but return a user-friendly message
        print(f"Error calling OpenRouter API: {e}")
        return f"❌ OpenRouter API error: {str(e)}"
    except (KeyError, IndexError):
        # Handle unexpected JSON structure from the API
        print(f"ERROR: Unexpected GPT response format. Response: {result}")
        return "❌ Unexpected GPT response format."