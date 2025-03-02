import { Pinecone } from '@pinecone-database/pinecone'
import { config } from 'dotenv'

config()

export const pineconeClient = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY as string
})
