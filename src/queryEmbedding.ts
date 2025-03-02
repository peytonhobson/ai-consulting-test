import { pineconeClient } from './pineconeClient'

export async function queryEmbedding(vector: number[], topK: number = 5) {
  const index = pineconeClient.Index('business-documents')

  const result = await index.query({
    vector,
    topK,
    includeMetadata: true
  })

  return result.matches
}
