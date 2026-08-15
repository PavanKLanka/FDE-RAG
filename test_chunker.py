from src.chunker import chunk_text

documents_chuncked = chunk_text("data/knowledge_base")

print("Documents found:", len(documents_chuncked))

for document in documents_chuncked:
    print(documents_chuncked)