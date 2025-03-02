import { OpenAI } from 'openai'
import { config } from 'dotenv'

config()

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
})

// Generate embeddings using OpenAI API

export async function generateEmbedding(
  text: string
): Promise<number[] | undefined> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-ada-002',
    input: text
  })

  return response.data[0]?.embedding
}
