from src.embeddings import EmbeddingModel
 
embedding_model = EmbeddingModel()
documents_embedded = embedding_model.embed(["Abc"])


print(
    "Documents Embedded:",
    len(documents_embedded)
)


print(
    "Embedding dimensions:",
    documents_embedded.shape
)