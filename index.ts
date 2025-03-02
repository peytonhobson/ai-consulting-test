import { SQS } from 'aws-sdk'
import { config } from 'dotenv'
import { processMessage } from './src/processMessage'

config()

const sqs = new SQS()

const QueueUrl = process.env.QUEUE_URL as string

// Mainconfig,  function to poll messages from SQS and process them
async function main() {
  // eslint-disable-next-line no-constant-condition
  while (true) {
    try {
      // Receive messages from SQS
      const response = await sqs
        .receiveMessage({
          QueueUrl,
          MaxNumberOfMessages: 10,
          WaitTimeSeconds: 10
        })
        .promise()

      if (response.Messages) {
        for (const message of response.Messages) {
          await processMessage(message)

          if (message.ReceiptHandle) {
            // Delete message after processing
            await sqs
              .deleteMessage(
                {
                  QueueUrl,
                  ReceiptHandle: message.ReceiptHandle
                },
                () => {}
              )
              .promise()
          }
        }
      }
    } catch (error) {
      console.error('Error polling messages:', error)
    }
  }
}

// Start the service
main().catch(err => console.error('Service failed:', err))
