from typing import List
from dotenv import load_dotenv
from clients.openai_embeddings import openai_embeddings_client
from clients.pinecone_client import pinecone_index

load_dotenv()


async def generate_document_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI API."""
    try:

        response = openai_embeddings_client.embed_documents(texts)

        print(f"Successfully generated {len(response)} embeddings")
        return response
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        import traceback

        traceback.print_exc()
        return []


def upsert_embeddings(id: str, vector: list, metadata: dict):
    """
    Upsert a vector embedding into Pinecone index.

    Args:
        id: Unique identifier for the vector
        vector: The embedding vector
        metadata: Additional metadata to store with the vector

    Returns:
        None
    """
    try:
        # Upsert the vector to Pinecone
        pinecone_index.upsert(
            vectors=[{"id": id, "values": vector, "metadata": metadata}]
        )

        return True
    except Exception as e:
        print(f"Error upserting embedding {id}: {e}")

        return False


async def generate_query_embedding(text: str) -> List[float]:
    """Generate a single embedding for a user query using OpenAI API."""
    try:
        # Generate embedding for a single query
        embeddings = await generate_document_embeddings([text])
        if embeddings and len(embeddings) > 0:
            return embeddings[0]
        return []
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        import traceback

        traceback.print_exc()
        return []
