from sentence_transformers import SentenceTransformer


# Load the embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text):
    """
    Convert text into an embedding vector.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    embedding = model.encode(
        text,
        convert_to_numpy=True
    )

    return embedding


def generate_embeddings(chunks):
    """
    Generate embeddings for multiple text chunks.
    """
    if not chunks:
        return []

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    )

    return embeddings


if __name__ == "__main__":

    test_text = (
        "Two workers were found without safety helmets."
    )

    embedding = generate_embedding(test_text)

    print("Embedding generated successfully!")
    print("Vector dimensions:", len(embedding))
    print("First 10 values:")
    print(embedding[:10])