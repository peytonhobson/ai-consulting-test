from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from src.clients.openai_embeddings import openai_embeddings_client
from src.clients.pinecone_client import pinecone_client

load_dotenv()

INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'business-documents-test')
index = pinecone_client.Index(INDEX_NAME)

async def query_similar_records(query: str, top_k: int = 5) -> Optional[List[Dict[str, Any]]]:
    """Query similar records from Pinecone using embedding."""
    # Generate embedding for the query
    embedding = await openai_embeddings_client.embed_query(query)
    
    if not embedding:
        return None

    # Query the index
    query_response = await index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )

    return query_response.matches

async def upsert_embeddings(id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
    """Upsert embeddings to Pinecone."""
    await index.upsert([{
        'id': id,
        'values': vector,
        'metadata': metadata
    }])
