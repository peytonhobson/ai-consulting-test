import os
import boto3
from dotenv import load_dotenv
from src.utils import process_message

load_dotenv()

# Initialize AWS SQS client
sqs = boto3.client(
    'sqs',
    region_name='us-east-1'
)

QUEUE_URL = os.getenv('QUEUE_URL')

async def process_sqs_messages():
    """Poll and process messages from SQS queue."""
    try:
        has_more_messages = True

        while has_more_messages:
            # Receive messages from SQS
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10
            )

            messages = response.get('Messages', [])
            
            if not messages:
                has_more_messages = False
                continue

            for message in messages:
                receipt_handle = message.get('ReceiptHandle')
                
                if not receipt_handle:
                    continue

                successfully_processed = await process_message(message)

                if successfully_processed:
                    # Delete message after successful processing
                    sqs.delete_message(
                        QueueUrl=QUEUE_URL,
                        ReceiptHandle=receipt_handle
                    )
                else:
                    print(f"Failed to process message: {message.get('MessageId')}")
                    # TODO: Implement alert mechanism for failed messages

    except Exception as error:
        print('Error polling messages:', error)

if __name__ == "__main__":
    import asyncio
    asyncio.run(process_sqs_messages())
