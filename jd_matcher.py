from sentence_transformers import SentenceTransformer, util

# Load model once (slow step), outside any function
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    if not text.strip():
        return None
    return model.encode(text, convert_to_tensor=True)

def calculate_similarity(resume_text: str, jd_text: str) -> float:
    resume_emb = get_embedding(resume_text)
    jd_emb = get_embedding(jd_text)

    if resume_emb is None or jd_emb is None:
        return 0.0

    similarity = util.pytorch_cos_sim(resume_emb, jd_emb)
    return float(similarity.item())
