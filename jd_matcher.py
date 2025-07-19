# jd_matcher.py

from sentence_transformers import SentenceTransformer, util
import gc # Import garbage collection for potential minor help

# CRITICAL: This model is loaded globally, meaning it's loaded once when the
# jd_matcher module is imported (i.e., when your Flask app starts).
# Ensure you are using the 'all-MiniLM-L6-v2' model as it's one of the smallest.
# If you use a larger model here, you WILL run out of memory on Render's free tier.
model = SentenceTransformer('all-MiniLM-L6-v2')
print(f"INFO: SentenceTransformer model 'all-MiniLM-L6-v2' loaded.")

def get_embedding(text: str):
    """
    Generates sentence embeddings for the given text.
    Handles empty text gracefully.
    """
    if not text or not text.strip():
        return None
    
    return model.encode(text, convert_to_tensor=True)

def calculate_similarity(resume_text: str, jd_text: str) -> float:
    """
    Calculates cosine similarity between resume and job description embeddings.
    """
    resume_emb = get_embedding(resume_text)
    jd_emb = get_embedding(jd_text)

    # If either embedding is None (due to empty text), return 0.0 similarity
    if resume_emb is None or jd_emb is None:
        return 0.0

    similarity = util.pytorch_cos_sim(resume_emb, jd_emb)
    result_similarity = float(similarity.item())

    # Optional: Explicitly delete tensors and trigger garbage collection
    # In a single-threaded environment, Python's GC is usually sufficient,
    # but in tight memory situations, this can sometimes help free memory faster.
    del resume_emb
    del jd_emb
    del similarity
    gc.collect()

    return result_similarity