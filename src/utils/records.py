from clients import openai_chat_client, pinecone_index
from utils.embeddings import generate_query_embedding
from flashrank import Ranker, RerankRequest
import os

cache_dir = "./cache/flashrank"
os.makedirs(cache_dir, exist_ok=True)

# Instantiate the Ranker at module level
ranker = Ranker(model_name="rank-T5-flan", cache_dir=cache_dir)


async def query_similar_records(user_prompt: str):
    """
    Find relevant documents for the user's question using multiple search strategies
    """
    # Step 1: Generate different versions of the user's question to improve search
    expand_prompt = f"Rephrase this query in 2 different ways to help find relevant information:\nQuery: {user_prompt}"

    expand_response = openai_chat_client.responses.create(
        model="gpt-4o",
        input=expand_prompt,
    )

    # Extract the rephrased queries from the new response structure
    rephrased_queries = []
    if expand_response.output and len(expand_response.output) > 0:
        message = expand_response.output[0]
        if message.content and len(message.content) > 0:
            for content_item in message.content:
                if content_item.type == "output_text":
                    rephrased_queries.extend(
                        [q.strip() for q in content_item.text.split("\n") if q.strip()]
                    )

    expanded_queries = [user_prompt] + rephrased_queries

    # Step 2: Search for relevant documents using each query
    all_docs = []
    for query in expanded_queries:
        query_vector = await generate_query_embedding(query)
        if query_vector:
            results = pinecone_index.query(
                namespace="",
                vector=query_vector,
                top_k=12,
                include_metadata=True,
                include_values=True,
            )

            if results.get("matches"):
                all_docs.extend(results["matches"])

    # Remove duplicate documents based on chunk_text (with fallback to empty string)
    unique_docs = list(
        {doc["metadata"].get("chunk_text", ""): doc for doc in all_docs}.values()
    )

    # Re-rank unique_docs using rank-T5-flan to select the top 6
    if unique_docs:
        try:
            passages = [{"text": doc["metadata"]["chunk_text"]} for doc in unique_docs]
            rerank_request = RerankRequest(query=user_prompt, passages=passages)
            reranked = ranker.rerank(rerank_request)

            # Use a safer approach to get indices
            final_docs = []
            for i in range(min(6, len(reranked))):
                if i >= len(unique_docs):
                    break
                final_docs.append(unique_docs[i])
        except Exception as e:
            print(f"Error during reranking: {e}")
            # Fallback to top 6 (or fewer) docs without reranking
            final_docs = unique_docs[: min(6, len(unique_docs))]
    else:
        final_docs = []

    # Return formatted context from the documents
    return [
        f"Source: {doc['metadata'].get('title', 'Unknown')}\n"
        f"Content: {doc['metadata'].get('chunk_text', '')}\n"
        f"Location: {doc['metadata'].get('source', 'Unknown')}"
        for doc in final_docs
    ]
