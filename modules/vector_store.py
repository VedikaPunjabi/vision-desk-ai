import chromadb
from .embeddings import generate_embeddings


# Create a persistent ChromaDB database
client = chromadb.PersistentClient(path="vector_db")

# Create/get our knowledge collection
collection = client.get_or_create_collection(
    name="inspection_documents"
)


def store_chunks(chunks, source_file):
    """
    Generate embeddings and store document chunks in ChromaDB.

    Prevents duplicate processing of the same source file.
    """

    if not chunks:
        raise ValueError("No chunks provided.")

    # Check whether this document already exists
    existing = collection.get(
        where={
            "source": source_file
        }
    )

    existing_ids = existing.get("ids", [])

    if existing_ids:
        print(
            f"Document '{source_file}' already exists "
            f"in the knowledge repository."
        )

        return 0

    # Generate embeddings
    embeddings = generate_embeddings(chunks)

    # Unique IDs for this document
    ids = [
        f"{source_file}_{i}"
        for i in range(len(chunks))
    ]

    # Metadata
    metadatas = [
        {
            "source": source_file,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    # Store in ChromaDB
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    return len(chunks)

def search_chunks(query, n_results=3):
    """
    Search the knowledge repository using semantic similarity.
    """

    query_embedding = generate_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )

    return results


if __name__ == "__main__":

    test_chunks = [
        "Two workers were found without safety helmets.",
        "One emergency exit was partially blocked.",
        "Fire extinguisher inspection was overdue.",
        "All workers must wear appropriate PPE."
    ]

    source_file = "test_report.pdf"

    stored = store_chunks(
        test_chunks,
        source_file
    )

    print(f"Stored {stored} chunks successfully.")

    print("\n===== SEMANTIC SEARCH TEST =====")

    query = "What safety problems were found?"

    results = search_chunks(query)

    for i, document in enumerate(results["documents"][0]):
        print(f"\nResult {i + 1}:")
        print(document)