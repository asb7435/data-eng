# qd_collection.py — 임베딩 차원에 맞춰 컬렉션을 만듭니다
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from rag_env import get_emb

emb = get_emb()
client = QdrantClient(url="http://localhost:6333")

COLLECTION = "lecture_notes"
DIM = len(emb.embed_query("차원 확인"))   # 임베딩 모델의 차원과 반드시 일치해야 합니다

if not client.collection_exists(COLLECTION):
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=DIM, distance=Distance.COSINE),
    )

print(client.get_collection(COLLECTION).config.params.vectors)
