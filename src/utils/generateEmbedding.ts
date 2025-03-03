import { config } from 'dotenv'
import { openaiClient } from '../clients/openai'

config()

// Generate embeddings using OpenAI API

export async function generateEmbedding(
  text: string
): Promise<number[] | undefined> {
  const response = await openaiClient.embeddings.create({
    model: 'text-embedding-ada-002',
    input: text
  })

  return response.data[0]?.embedding
}
