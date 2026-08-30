from sentence_transformers import SentenceTransformer
import os

EMBED_MODEL_NAME = "Alibaba-NLP/gte-modernbert-base"
EMBED_DIM = 768
_CACHE_DIR = "./_models"
def init_embedder():

    if not os.path.exists(_CACHE_DIR):
        model = SentenceTransformer(
                EMBED_MODEL_NAME,
                cache_folder=_CACHE_DIR,
                device="cuda",
                trust_remote_code=True,
            )
        return model
if __name__ == "__main__":
    if os.path.exists(_CACHE_DIR):
        print("Exists")