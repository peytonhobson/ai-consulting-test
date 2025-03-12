from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

openai_embeddings_client = OpenAIEmbeddings(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="text-embedding-3-small",
    # TODO: May need to dynamically correspond dimensions to pinecone index at runtime
    dimensions=1536,
)
