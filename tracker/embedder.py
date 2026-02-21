# tracker/embedder.py
import numpy as np
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str) -> np.ndarray:
        if not text:
            return np.zeros(384, dtype=float)
        emb = self.model.encode(
            text,
            show_progress_bar=False,
            convert_to_numpy=True  # 🔥 THIS IS THE KEY
        )

        return emb.astype(np.float32)
