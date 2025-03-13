import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# TODO: Temporary client. Use langchain open ai client if available with assistants
assistant_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
