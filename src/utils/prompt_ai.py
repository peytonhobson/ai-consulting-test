from langchain_core.messages import HumanMessage, AIMessage
from clients import openai_chat_client, pinecone_index
import numpy as np
from utils.embeddings import generate_query_embedding
from math_branch import process_math_query  # Import the math branch function

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

    # Use MMR to select diverse, relevant documents
    if len(unique_docs) > 1:
        if "values" in unique_docs[0] and unique_docs[0]["values"]:
            doc_embeddings = np.array([doc["values"] for doc in unique_docs])

        query_embedding = await generate_query_embedding(user_prompt)
        if not query_embedding:
            return []

        # Select documents using MMR
        selected_indices = calculate_mmr(
            doc_embeddings, query_embedding, lambda_param=0.7, top_k=6
        )
        final_docs = [unique_docs[i] for i in selected_indices]
    else:
        final_docs = unique_docs[:6]

    # Return formatted context from the documents
    return [
        f"Source: {doc['metadata'].get('title', 'Unknown')}\n"
        f"Content: {doc['metadata'].get('chunk_text', '')}\n"
        f"Location: {doc['metadata'].get('source', 'Unknown')}"
        for doc in final_docs
    ]

async def prompt_ai(messages):
    """
    Main function that:
    1. Determines if the query is math-related
    2. If math-related, uses the math branch to process the query
    3. If not math-related, uses the original RAG pipeline
    """
    # Get the user's latest question
    user_prompt = messages[-1].content

    # Define math-related keywords
    math_keywords = [
        "calculate", "sum", "addition", "subtraction",
        "multiplication", "division", "npv", "irr", "pv", "fv", "math"
    ]
    # Check if the query contains any math keywords (case-insensitive)
    is_math = any(keyword in user_prompt.lower() for keyword in math_keywords)

    # Retrieve context for both math and non-math queries
    retrieved_context = await query_similar_records(user_prompt)
    print("retrieved_context", retrieved_context)  # Optional logging

    if is_math:
        # Handle math-related query
        answer = await process_math_query(user_prompt, retrieved_context)
        return AIMessage(content=answer)
    else:
        # Handle non-math query using original RAG logic
        default_text = "This is a default sample text because no documents were provided."
        if retrieved_context and default_text in retrieved_context[0]:
            formatted_prompt = user_prompt
            verification_needed = False
        else:
            formatted_prompt = (
                f"Based on the following documents:\n{retrieved_context}\n\n"
                f"Answer the question:\n{user_prompt}"
            )
            verification_needed = True

        # Get initial answer from AI
        conversation = messages + [HumanMessage(content=formatted_prompt)]
        initial_response = openai_chat_client(conversation)
        answer = initial_response.content

        # Verify answer accuracy if context was used
        if verification_needed:
            verify_prompt = (
                f"Documents:\n{retrieved_context}\n\n"
                f"Answer: {answer}\n\n"
                "Is this answer accurate and well supported by the documents? "
                "(Respond with 'yes' or 'no' and a brief explanation.)"
            )
            verification_response = openai_chat_client(
                [HumanMessage(content=verify_prompt)]
            )
            verification = verification_response.content.lower()

            # Determine confidence based on verification
            confidence = 1.0 if "yes" in verification else 0.5
            final_answer = (
                answer
                if confidence >= 0.5
                else "I'm not sure about this answer. Please reach out VIA email for additional assistance."
            )
        else:
            final_answer = answer

        return AIMessage(content=final_answer)