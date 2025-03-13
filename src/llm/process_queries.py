import os
from openai import OpenAI, APIError
import time

# Synchronous OpenAI client for Assistant API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def process_query(thread_id, user_prompt, retrieved_context=None):
    """Process a query using the OpenAI Assistant API."""
    start_time = time.time()

    try:
        # Check if a run is active - only enter polling loop if needed
        active_runs = client.beta.threads.runs.list(thread_id=thread_id, limit=1)

        # Only enter waiting loop if there's actually an active run
        if active_runs.data and active_runs.data[0].status in [
            "in_progress",
            "queued",
            "requires_action",
        ]:
            active_run = active_runs.data[0]
            print(f"Waiting for run {active_run.id} to complete...")

            # Poll until the run is complete with a smarter polling strategy
            wait_time = 0.2  # Start with 200ms wait
            while active_run.status in ["in_progress", "queued", "requires_action"]:
                active_run = client.beta.threads.runs.retrieve(
                    thread_id=thread_id, run_id=active_run.id
                )
                if active_run.status not in [
                    "in_progress",
                    "queued",
                    "requires_action",
                ]:
                    break

                # Use adaptive polling: increase wait time as we wait longer
                wait_time = min(wait_time * 1.5, 1.0)  # Cap at 1 second
                time.sleep(wait_time)

            print(f"Run {active_run.id} completed with status: {active_run.status}")
        else:
            print("No active runs, proceeding with query")

        # Add timing checkpoint
        check_time = time.time() - start_time
        print(f"Run check completed in {check_time:.2f}s")

        # Add context as a system message if available
        if retrieved_context:
            context_message = f"Context for answering: {retrieved_context}"
            client.beta.threads.messages.create(
                thread_id=thread_id, role="user", content=context_message
            )

        # Add the user's question
        client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_prompt
        )

        # Run the assistant
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
        )

        if run.status == "failed":
            return "I encountered an error processing your request."

        # Get code and output from run steps if available
        run_steps = client.beta.threads.runs.steps.list(
            thread_id=thread_id, run_id=run.id
        )

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

        # Get the latest assistant message (not user message)
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        if not messages.data:
            return "No response received."

        # Find the most recent assistant message AFTER creating the run
        # The run ID can help identify messages that came after our query
        latest_message = None
        for msg in messages.data:
            if msg.role == "assistant":
                latest_message = msg.content[0].text.value
                break

        if not latest_message:
            return "No assistant response found."

        # Format with HTML dropdown if code is present
        if code:
            formatted_answer = (
                f"{latest_message}\n\n"
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
            formatted_answer = latest_message

        total_time = time.time() - start_time
        print(f"Total query processing time: {total_time:.2f}s")

        return formatted_answer

    except APIError as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"


def get_thread_messages(thread_id):
    """
    Retrieve all messages from a thread.

    Args:
        thread_id: The ID of the thread

    Returns:
        List of messages with role and content
    """
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        formatted_messages = []

        for msg in reversed(messages.data):  # Reverse to get chronological order
            role = "ai" if msg.role == "assistant" else "human"
            content = msg.content[0].text.value if msg.content else ""
            formatted_messages.append({"type": role, "content": content})

        return formatted_messages
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return []
