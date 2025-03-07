import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# Create an instance of the Pinecone client
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

# Optionally, check if the index exists and create it if needed.
indexes = [index.name for index in pc.list_indexes()]
if "business-documents-test" not in indexes:
    pc.create_index(
        name="business-documents-test",
        dimension=1536,            
        metric="cosine",           
        spec=ServerlessSpec(
            cloud=os.getenv("PINECONE_CLOUD", "gcp"),
            region=os.getenv("PINECONE_REGION", "us-east1-gcp")
        )
    )

# Get a handle to the index and assign it to pinecone_client
pinecone_client = pc.Index("business-documents-test")
