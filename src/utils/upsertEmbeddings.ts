import { pineconeClient } from '../clients/pinecone'
import type { RecordMetadata } from '@pinecone-database/pinecone'

// TODO: Make index env var for reusability
const index = pineconeClient.Index('business-documents-test')

export async function upsertEmbedding({
  id,
  vector,
  metadata
}: {
  id: string
  vector: number[]
  metadata: RecordMetadata
}) {
  await index.upsert([
    {
      id,
      values: vector,
      metadata
    }
  ])
}
