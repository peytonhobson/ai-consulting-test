from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

openai_chat_client = ChatOpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    model="gpt-4o"
)
