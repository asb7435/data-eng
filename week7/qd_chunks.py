# qd_chunks.py — long_notes.txt 를 7-2 에서 정한 크기(300 · 30)로 잘라 적재
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from rag_env import get_emb

emb = get_emb()
client = QdrantClient(url="http://localhost:6333")

docs = TextLoader("long_notes.txt", encoding="utf-8").load()
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_documents(docs)
print("조각:", len(chunks))

NOTES = "my_notes"
DIM = len(emb.embed_query("차원 확인"))
if not client.collection_exists(NOTES):
    client.create_collection(
        collection_name=NOTES,
        vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
    )

vectors = emb.embed_documents([c.page_content for c in chunks])
client.upsert(
    collection_name=NOTES,
    points=[
        PointStruct(id=i, vector=v,
                    payload={"text": c.page_content, **c.metadata})
        for i, (c, v) in enumerate(zip(chunks, vectors))
    ],
)
print(client.count(NOTES))
