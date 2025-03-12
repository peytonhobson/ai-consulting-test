from .process_queries import process_query
from utils import query_similar_records


async def handle_prompt(thread_id, user_prompt):
    """
    Handle a user prompt by retrieving context and processing the query.

    Args:
        thread_id: The thread ID to use
        user_prompt: The user's question

    Returns:
        The formatted response
    """
    # Retrieve context for the query
    retrieved_context = await query_similar_records(user_prompt)

    # Process the query with the assistant
    answer = await process_query(thread_id, user_prompt, retrieved_context)

    return answer
