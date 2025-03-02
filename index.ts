import AWS from 'aws-sdk'
import { config } from 'dotenv'
import { processMessage } from './src/processMessage'

config()

const sqs = new AWS.SQS({
  region: 'us-east-1'
})

const QueueUrl = process.env.QUEUE_URL as string

// Mainconfig,  function to poll messages from SQS and process them
async function main() {
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
        const successfullyProcessed = await processMessage(message)

        // TODO: How can we have more robust polling and error mechanisms?
        if (message.ReceiptHandle && successfullyProcessed) {
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

setInterval(async () => {
  try {
    await main()
  } catch (e) {
    console.error(e)
  }
}, 10000)
