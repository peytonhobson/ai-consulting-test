from typing import List
import os
from dotenv import load_dotenv
from src.clients.openai_embeddings import openai_embeddings_client

load_dotenv()

async def generate_document_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI API."""
    response = await openai_embeddings_client.embed_documents(texts)
    return response
