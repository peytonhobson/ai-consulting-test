import AWS from 'aws-sdk'
import { config } from 'dotenv'
import { processMessage } from '../utils/processMessage'

config()

const sqs = new AWS.SQS({
  region: 'us-east-1'
})

const QueueUrl = process.env.QUEUE_URL as string

// Function to poll messages from SQS and process them
async function main() {
  try {
    let hasMoreMessages = true

    while (hasMoreMessages) {
      // Receive messages from SQS
      const response = await sqs
        .receiveMessage({
          QueueUrl,
          MaxNumberOfMessages: 10,
          WaitTimeSeconds: 10
        })
        .promise()

      if (response.Messages && response.Messages.length > 0) {
        for (const message of response.Messages) {
          const successfullyProcessed = await processMessage(message)

          // TODO: Create an alert mechanism here if a message isn't
          // successfully processed. We should then process the message manually.
          if (message.ReceiptHandle && successfullyProcessed) {
            // Delete message after processing
            await sqs
              .deleteMessage({
                QueueUrl,
                ReceiptHandle: message.ReceiptHandle
              })
              .promise()
          }
        }
      } else {
        // No more messages to process
        hasMoreMessages = false
      }
    }
  } catch (error) {
    console.error('Error polling messages:', error)
  }
}

// Execute the main function
main().catch(e => console.error(e))
