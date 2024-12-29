# utils.py

def chunkify(text: str, max_length: int) -> list[str]:
    sentences = text.split(". ")
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence) + 2
        if current_length + sentence_length > max_length:
            chunks.append(". ".join(current_chunk) + ".")
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(". ".join(current_chunk) + ".")

    return chunks
