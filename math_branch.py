import os
import time
from openai import OpenAI, APIError

# Synchronous OpenAI client for Assistant API (can be made async if needed)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_code_interpreter(query: str, timeout: int = 30) -> dict:
    """
    Call the OpenAI Assistant with Code Interpreter to process a math query.
    Returns a dict with the answer, Python code, and output.
    """
    try:
        # Create a thread
        thread = client.beta.threads.create()

        # Send the user query
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        # Create and run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
            tools=[{"type": "code_interpreter"}]  # Explicitly enable Code Interpreter
        )

        # Wait for run completion
        start_time = time.time()
        while run.status not in ["completed", "failed"]:
            if time.time() - start_time > timeout:
                return {"answer": "Calculation timed out.", "code": "", "output": ""}
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "failed":
            return {"answer": "Run failed.", "code": "", "output": ""}

        # Fetch run steps to get code and output
        run_steps = client.beta.threads.runs.steps.list(thread_id=thread.id, run_id=run.id)
        code = ""
        output = ""
        for step in run_steps.data:
            if step.step_details.type == "tool_calls":
                for tool_call in step.step_details.tool_calls:
                    if tool_call.type == "code_interpreter":
                        code = tool_call.code_interpreter.input or ""
                        if tool_call.code_interpreter.outputs:
                            for out in tool_call.code_interpreter.outputs:
                                if out.type == "logs":
                                    output += out.logs + "\n"

        # Fetch the final assistant message
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        final_message = "No response received."
        if messages.data and messages.data[0].content:
            final_message = messages.data[0].content[0].text.value

        return {
            "answer": final_message,
            "code": code,
            "output": output.strip()
        }

    except APIError as e:
        return {"answer": f"API Error: {str(e)}", "code": "", "output": ""}
    except Exception as e:
        return {"answer": f"Unexpected Error: {str(e)}", "code": "", "output": ""}

async def process_math_query(user_prompt: str, retrieved_context: list) -> str:
    """
    Process a math query using the Code Interpreter and format the response with a dropdown.
    Returns a string, potentially with HTML for the dropdown.
    """
    if retrieved_context:
        joined_context = "\n\n".join(retrieved_context)
        math_prompt = (
            "The following documents may contain numeric data relevant to the math question:\n"
            f"{joined_context}\n\n"
            "Based on the above data and the math question below, write Python code to extract the necessary "
            "numeric values and perform the appropriate math operation. Execute the code and print the final result "
            "using print() to ensure the output is captured (no extra commentary in the output).\n\n"
            f"Math Question: {user_prompt}"
        )
    else:
        math_prompt = (
            "Based on the math question below, write Python code to perform the appropriate math operation and execute it. "
            "Print the final result using print() to ensure the output is captured (no extra commentary in the output).\n\n"
            f"Math Question: {user_prompt}"
        )

    response = call_code_interpreter(math_prompt)
    answer = response["answer"]
    code = response["code"]
    output = response["output"]

    # Format with HTML dropdown if code is present
    if code:
        formatted_answer = (
            f"{answer}\n\n"
            "<details>\n"
            "<summary>View Python code and output</summary>\n\n"
            "```python\n"
            f"{code}\n"
            "```\n\n"
            "Output:\n"
            f"{output or 'No output captured.'}\n"
            "</details>"
        )
    else:
        formatted_answer = answer

    return formatted_answer