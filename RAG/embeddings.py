from langchain_community.embeddings import FakeEmbeddings

def generate_embeddings():
    try:
        embeddings = FakeEmbeddings(size=1352)
        return embeddings
    except Exception as e:
        print("Unable to process Embeddings", e)
