import { pineconeClient } from './pineconeClient'

export async function queryEmbedding(vector: number[], topK: number = 5) {
  //TODO: env var
  const index = pineconeClient.Index('business-documents-test')

  const result = await index.query({
    vector,
    topK,
    includeMetadata: true
  })

  return result.matches
}
