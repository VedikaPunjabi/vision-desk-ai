import os
from .document_processor import extract_text
from .chunker import chunk_text
from .vector_store import store_chunks


def process_document(file_path):
    """
    Complete document processing pipeline:

    File
      ↓
    Text extraction
      ↓
    Cleaning
      ↓
    Chunking
      ↓
    Embeddings
      ↓
    ChromaDB
    """

    # Check whether file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    # Get uploaded filename
    filename = os.path.basename(file_path)

    # -------------------------------------------------
    # Remove UUID prefix from uploaded filenames
    #
    # Example:
    # 26c8c724abcd1234..._test_report.pdf
    # becomes:
    # test_report.pdf
    # -------------------------------------------------

    if "_" in filename:

        possible_uuid, original_name = filename.split(
            "_",
            1
        )

        if len(possible_uuid) == 32:
            filename = original_name

    # -------------------------------------------------
    # Step 1: Extract and clean text
    # -------------------------------------------------

    text = extract_text(file_path)

    if not text.strip():
        raise ValueError(
            "No readable text was found in the document."
        )

    # -------------------------------------------------
    # Step 2: Create chunks
    # -------------------------------------------------

    chunks = chunk_text(
        text,
        chunk_size=500,
        overlap=100
    )

    if not chunks:
        raise ValueError(
            "No text chunks could be created."
        )

    # -------------------------------------------------
    # Step 3: Store chunks + embeddings in ChromaDB
    # -------------------------------------------------

    stored_count = store_chunks(
        chunks,
        filename
    )

    # -------------------------------------------------
    # Return processing information
    # -------------------------------------------------

    return {
        "filename": filename,
        "characters": len(text),
        "chunks": len(chunks),
        "stored": stored_count
    }


# -----------------------------------------------------
# TEST THE COMPLETE PIPELINE
# -----------------------------------------------------

if __name__ == "__main__":

    test_file = "test_report.pdf"

    try:

        result = process_document(
            test_file
        )

        print(
            "\n===== DOCUMENT PROCESSING COMPLETE ====="
        )

        print(
            f"File: {result['filename']}"
        )

        print(
            f"Characters extracted: "
            f"{result['characters']}"
        )

        print(
            f"Chunks created: "
            f"{result['chunks']}"
        )

        print(
            f"Chunks stored: "
            f"{result['stored']}"
        )

    except Exception as e:

        print(
            f"\nERROR: {e}"
        )