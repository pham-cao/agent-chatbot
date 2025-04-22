from qdrant_client import QdrantClient
from decouple import config
from qdrant_client.models import VectorParams, Distance
from RAG.LLMs import doc_embeddings_model
from langchain_text_splitters import CharacterTextSplitter
from langchain_qdrant import QdrantVectorStore

from uuid import uuid4

QDRANT_HOST = config('QDRANT_HOST')
QDRANT_POST = config('QDRANT_PORT')

DB_CLIENT = QdrantClient(host=QDRANT_HOST,
                         port=QDRANT_POST)


class ProcessVectorDB:
    def __init__(self):
        self.client = DB_CLIENT

    def insert(self, content: str, collection_name: str):
        self.client.create_collection(collection_name=collection_name,
                                      vectors_config=VectorParams(size=768,
                                                                  distance=Distance.COSINE))

        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=doc_embeddings_model,
        )

        splitter = CharacterTextSplitter(separator="\n\n",
                                         chunk_size=1000,
                                         chunk_overlap=200,
                                         length_function=len,
                                         is_separator_regex=False,
                                         )

        chunks = splitter.create_documents([content])
        uuids = [str(uuid4()) for _ in range(len(chunks))]
        vector_store.add_documents(documents=chunks, ids=uuids)

    def search_query(self, collection_name, query):
        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=doc_embeddings_model,
        )
        results = vector_store.similarity_search(query, k=2)
        return results

    def delete(self, collection_name: str):
        self.client.delete_collection(collection_name=collection_name)

    def get_collections(self):
        collections = self.client.get_collections()
        return {"Name": [collection.name for collection in collections.collections]}
