import os
from openai import OpenAI

# TODO: Temporary client. Use langchain open ai client if available with assistants
assistant_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
