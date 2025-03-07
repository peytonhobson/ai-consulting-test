import json
import boto3
from typing import Optional
import os
from dotenv import load_dotenv
import asyncio

from .document_processor import process_document
from .embeddings import generate_document_embeddings
from .shared import upsert_embeddings

load_dotenv()

s3 = boto3.client('s3')

async def process_message(message: dict) -> bool:
    """Process a single message from SQS."""
    try:
        message_body = message.get('Body')
        if not message_body:
            return False

        body = json.loads(message_body)
        bucket_name = body['bucket']
        object_key = body['key']

        print(f'Processing file from bucket "{bucket_name}" with key "{object_key}"')

        # Download file from S3
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')

        chunked_file_content = process_document(file_content)

        # Generate embedding for file content
        embeddings = await generate_document_embeddings(
            [content.page_content for content in chunked_file_content]
        )

        if not embeddings:
            return False

        # Upsert embeddings for each chunk
        await asyncio.gather(*[
            upsert_embeddings(
                id=f"{object_key}-chunk-{index}",
                vector=chunk,
                metadata={"bucketName": bucket_name, "objectKey": object_key, "chunkIndex": index}
            )
            for index, chunk in enumerate(embeddings)
        ])

        print(f'Successfully upserted embedding for file "{object_key}"')
        return True

    except Exception as error:
        print('Error processing message:', error)
        return False