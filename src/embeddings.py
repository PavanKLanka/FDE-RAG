from sentence_transformers import SentenceTransformer


class EmbeddingModel:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def embed(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True
        )