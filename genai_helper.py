# genai_helper.py

from openai import OpenAI

# ✅ Step 1: Setup OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  # <-- replace with your OpenRouter key
)

# ✅ Step 2: Main function to call GPT
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
                "HTTP-Referer": "https://giteshresume.ai",   # required
                "X-Title": "GiteshResumeScreening"           # optional
            },
            model="deepseek/deepseek-chat",  # ✅ use any model from https://openrouter.ai/models
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
