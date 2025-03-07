from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

pinecone_client = Pinecone(
    api_key=os.getenv('PINECONE_API_KEY')
)
