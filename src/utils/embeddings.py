from typing import List
from dotenv import load_dotenv
from clients import openai_embeddings_client

load_dotenv()


async def generate_query_embedding(text: str) -> List[float]:
    """Generate a single embedding for a user query using OpenAI API."""
    try:
        # OpenAI's embed_query returns a single vector directly
        embeddings = openai_embeddings_client.embed_query(text)

        return embeddings
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        import traceback

        traceback.print_exc()
        return []
