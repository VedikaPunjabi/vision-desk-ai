import re


def split_into_sentences(text):
    """Split text into sentences while preserving meaningful content."""
    text = re.sub(r'\s+', ' ', text).strip()

    if not text:
        return []

    sentences = re.split(r'(?<=[.!?])\s+', text)

    return [sentence.strip() for sentence in sentences if sentence.strip()]


def chunk_text(text, chunk_size=500, overlap=100):
    """
    Create sentence-aware overlapping chunks.

    chunk_size: approximate maximum characters per chunk
    overlap: approximate number of characters repeated between chunks
    """

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:

        sentence_length = len(sentence)

        # Add sentence if it fits
        if current_chunk and current_length + sentence_length + 1 > chunk_size:

            chunks.append(" ".join(current_chunk))

            # Keep overlapping sentences
            overlap_chunk = []
            overlap_length = 0

            for previous_sentence in reversed(current_chunk):
                if overlap_length + len(previous_sentence) + 1 > overlap:
                    break

                overlap_chunk.insert(0, previous_sentence)
                overlap_length += len(previous_sentence) + 1

            current_chunk = overlap_chunk
            current_length = overlap_length

        current_chunk.append(sentence)
        current_length += sentence_length + 1

    # Add remaining sentences
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


if __name__ == "__main__":

    sample_text = """
    INSPECTION REPORT

    Date: 23 August 2026.

    Site: Manufacturing Unit A.

    Safety Observations:
    1. Two workers were found without safety helmets.
    2. One emergency exit was partially blocked.
    3. Fire extinguisher inspection was overdue.

    Recommendation:
    All workers must wear appropriate PPE.
    Emergency exits must remain clear at all times.
    Fire extinguishers should be inspected regularly.
    """

    chunks = chunk_text(
        sample_text,
        chunk_size=200,
        overlap=50
    )

    print(f"Total chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n===== CHUNK {i} =====")
        print(chunk)