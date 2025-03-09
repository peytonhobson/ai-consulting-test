from typing import List
from dotenv import load_dotenv
from clients import openai_embeddings_client

load_dotenv()


async def generate_query_embedding(text: str) -> List[float]:
    """Generate a single embedding for a user query using OpenAI API."""
    try:
        embeddings = openai_embeddings_client.embed_documents(text)

        if embeddings and len(embeddings) > 0:
            return embeddings[0]
        return []
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        import traceback

        traceback.print_exc()
        return []
