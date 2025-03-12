from clients import openai_chat_client, pinecone_index
from utils.embeddings import generate_query_embedding
import numpy as np
from langchain_core.messages import HumanMessage


def calculate_mmr(doc_embeddings, query_embedding, lambda_param=0.7, top_k=6):
    """
    Calculate Maximum Marginal Relevance (MMR) for document selection.
    lambda_param: Balance between relevance (similarity to query) and diversity
        - Higher lambda (closer to 1) = more relevance to query
        - Lower lambda (closer to 0) = more diversity
    top_k: Number of documents to return
    """
    selected_indices = []
    remaining_indices = list(range(len(doc_embeddings)))

    # Calculate how similar each document is to the query
    similarities = np.dot(doc_embeddings, query_embedding)

    # Select documents one by one
    for _ in range(top_k):
        if not remaining_indices:
            break

        # For each remaining document, calculate MMR score:
        # MMR = λ * (relevance to query) - (1-λ) * (similarity to already selected docs)
        mmr_scores = []
        for idx in remaining_indices:
            if not selected_indices:
                redundancy = 0  # First document has no redundancy
            else:
                # Find how similar this doc is to already selected docs
                redundancy = max(
                    np.dot(doc_embeddings[idx], doc_embeddings[j])
                    for j in selected_indices
                )
            mmr = lambda_param * similarities[idx] - (1 - lambda_param) * redundancy
            mmr_scores.append(mmr)

        # Pick the document with best balance of relevance and diversity
        next_idx = remaining_indices[np.argmax(mmr_scores)]
        selected_indices.append(next_idx)
        remaining_indices.remove(next_idx)

    return selected_indices


async def query_similar_records(user_prompt: str):
    """
    Find relevant documents for the user's question using multiple search strategies
    """
    # Step 1: Generate different versions of the user's question to improve search
    expand_prompt = f"Rephrase this query in 2 different ways to help find relevant information:\nQuery: {user_prompt}"
    expand_response = openai_chat_client([HumanMessage(content=expand_prompt)])
    expanded_queries = [user_prompt] + [
        q.strip() for q in expand_response.content.split("\n") if q.strip()
    ]

    # Step 2: Search for relevant documents using each query
    all_docs = []
    for query in expanded_queries:
        query_vector = await generate_query_embedding(query)
        if query_vector:
            results = pinecone_index.query(
                namespace="",
                vector=query_vector,
                top_k=15,
                include_metadata=True,
                include_values=True,
            )

            if results.get("matches"):
                all_docs.extend(results["matches"])

    # Remove duplicate documents based on chunk_text (with fallback to empty string)
    unique_docs = list(
        {doc["metadata"].get("chunk_text", ""): doc for doc in all_docs}.values()
    )

    # TODO: Add flash rerank

    final_docs = unique_docs[:6]

    # Return formatted context from the documents
    return [
        f"Source: {doc['metadata'].get('title', 'Unknown')}\n"
        f"Content: {doc['metadata'].get('chunk_text', '')}\n"
        f"Location: {doc['metadata'].get('source', 'Unknown')}"
        for doc in final_docs
    ]
