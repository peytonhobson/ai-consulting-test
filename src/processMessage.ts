import * as AWS from 'aws-sdk'
import { upsertEmbedding } from './upsertEmbeddings'
import { generateEmbedding } from './generateEmbedding'

const s3 = new AWS.S3()

// Process a single message from SQS
export async function processMessage(message: AWS.SQS.Message) {
  try {
    const messageBody = message.Body

    if (messageBody === undefined) {
      return
    }

    const body = JSON.parse(messageBody)
    const bucketName = body.bucketName
    const objectKey = body.objectKey

    console.log(
      `Processing file from bucket "${bucketName}" with key "${objectKey}"`
    )

    // Download file from S3
    const object = await s3
      .getObject({ Bucket: bucketName, Key: objectKey })
      .promise()
    const fileContent = object.Body?.toString('utf-8') || ''

    // Generate embedding for file content
    const embedding = await generateEmbedding(fileContent)

    if (embedding === undefined) {
      return
    }

    await upsertEmbedding({
      id: objectKey,
      vector: embedding,
      metadata: { bucketName, objectKey }
    })

    console.log(`Successfully upserted embedding for file "${objectKey}"`)
  } catch (error) {
    console.error('Error processing message:', error)
  }
}
