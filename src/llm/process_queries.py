from .instructions import instructions
from openai import APIError
from src.clients import openai_chat_client as client
from src.utils import query_similar_records
from dotenv import load_dotenv
import os

load_dotenv()


async def process_query(previous_response_id, user_prompt):
    """
    Process a query using the OpenAI Response API.

    Args:
        previous_response_id: The ID of the previous response (for multi-turn conversations)
        user_prompt: The user's question

    Returns:
        Tuple of (formatted_response, new_response_id)
    """
    try:
        retrieved_context = await query_similar_records(user_prompt)

        # Prepare the input message
        input_message = f"Context for answering: {retrieved_context}\n\n{user_prompt}"

        # Create the response using the OpenAI Response API
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            input=input_message,
            instructions=instructions,
            previous_response_id=previous_response_id,
        )

        # Extract the response content from the new structure
        response_content = ""
        if response.output and len(response.output) > 0:
            message = response.output[0]
            if message.content and len(message.content) > 0:
                for content_item in message.content:
                    if content_item.type == "output_text":
                        response_content += content_item.text

        response_id = response.id

        # TODO: Add back in once code interpreter is implemented
        # Check if there's any code output to format
        # code = ""
        # output = ""

        # If there are tool calls in the response, extract code and output
        # if hasattr(response, "tools") and response.tools:
        #     for tool in response.tools:
        #         if tool.type == "code_interpreter":
        #             if hasattr(tool, "code_interpreter") and tool.code_interpreter:
        #                 code = tool.code_interpreter.input or ""
        #                 if tool.code_interpreter.outputs:
        #                     for out in tool.code_interpreter.outputs:
        #                         if out.type == "logs":
        #                             output += out.logs + "\n"

        # Format with HTML dropdown if code is present
        # if code:
        #     formatted_answer = (
        #         f"{response_content}\n\n"
        #         "<details>\n"
        #         "<summary>View Python code and output</summary>\n\n"
        #         "```python\n"
        #         f"{code}\n"
        #         "```\n\n"
        #         "Output:\n"
        #         f"{output or 'No output captured.'}\n"
        #         "</details>"
        #     )
        # else:
        # formatted_answer = response_content

        return response_content, response_id

    except APIError as e:
        return f"API Error: {str(e)}", None
    except Exception as e:
        return f"Unexpected Error: {str(e)}", None
