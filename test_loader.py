from src.loader import load_documents

documents = load_documents("data/knowledge_base")

print("Documents found:", len(documents))

for document in documents:
    print(document["source"])