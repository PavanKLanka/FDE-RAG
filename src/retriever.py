import faiss
import numpy as np
#

class Retriever:

    def __init__(self, embeddings, chunks):

        self.chunks = chunks

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(
            np.array(
                embeddings
            ).astype("float32")
        )


    def search(
        self,
        query_embedding,
        top_k=3
    ):

        actual_top_k = min(
            top_k,
            len(self.chunks)
        )

        scores, indices = self.index.search(
            np.array(
                query_embedding
            ).astype("float32"),
            actual_top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index < 0:
                continue

            results.append({
                "score": float(score),
                "text": self.chunks[index]["text"],
                "source": self.chunks[index]["source"]
            })

        return results