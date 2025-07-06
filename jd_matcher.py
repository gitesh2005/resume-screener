from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return model.encode(text, convert_to_tensor=True)

def calculate_similarity(resume_text, jd_text):
    resume_emb = get_embedding(resume_text)
    jd_emb = get_embedding(jd_text)
    similarity = util.pytorch_cos_sim(resume_emb, jd_emb)
    return float(similarity.item())
