# genai_helper.py

import os
from openai import OpenAI
from dotenv import load_dotenv  # ✅ NEW

# ✅ Load .env file
load_dotenv()

# ✅ Fetch key & base_url from .env
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")  

# ✅ Setup OpenRouter client
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

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

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://giteshresume.ai",
                "X-Title": "GiteshResumeScreening"
            },
            model="deepseek/deepseek-chat",  # or any other model
            messages=[
                {"role": "system", "content": "You are a resume assistant"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"❌ OpenRouter Error: {str(e)}"
