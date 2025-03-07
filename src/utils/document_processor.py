from langchain_core.documents import Document

def clean_text(text: str) -> str:
    """Simple text cleaning: remove extra whitespace."""
    return ' '.join(text.split())

def chunk_text(text: str, chunk_size: int = 700, overlap_ratio: float = 0.3) -> list[str]:
    """Split text into overlapping chunks."""
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    chunks = []
    current_chunk = ''
    overlap_size = int(chunk_size * overlap_ratio)

    for sentence in sentences:
        if len(f"{current_chunk} {sentence}") > chunk_size and current_chunk:
            chunks.append(current_chunk)
            # Create overlap using last words
            words = current_chunk.split()
            overlap_words = ' '.join(words[-overlap_size:])
            current_chunk = f"{overlap_words} {sentence}"
        else:
            current_chunk += ('. ' if current_chunk else '') + sentence

    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def process_document(document_content: str) -> list[Document]:
    """Process document content into chunks with LangChain Documents."""
    cleaned = clean_text(document_content)
    chunks = chunk_text(cleaned)
    return [Document(page_content=chunk) for chunk in chunks]
