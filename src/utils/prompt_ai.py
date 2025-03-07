from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage

from src.clients.openai_chat import openai_chat_client
from .vector_search import query_similar_records

async def prompt_ai(messages: List[HumanMessage]) -> Optional[AIMessage]:
    """Process AI prompt with context from vector store."""
    user_prompt = messages[-1].content if messages else ""
    retrieved_context = await query_similar_records(user_prompt)

    if retrieved_context is None:
        formatted_prompt = user_prompt
    else:
        context_text = '\n'.join(match['values'] for match in retrieved_context)
        formatted_prompt = f"Based on the following documents:\n{context_text}\n\nAnswer the question:\n{user_prompt}"

    # Create conversation array
    conversation = [*messages, HumanMessage(content=formatted_prompt)]
    
    # Call the LLM
    response = await openai_chat_client.generate([conversation])
    
    content = response.generations[0][0].text if response.generations else None
    return AIMessage(content=content) if content else None
