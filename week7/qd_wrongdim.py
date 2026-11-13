# qd_wrongdim.py — 실습용으로 size=10 컬렉션에 진짜 벡터를 넣어 봅니다
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from rag_env import get_emb

emb = get_emb()
client = QdrantClient(url="http://localhost:6333")

if client.collection_exists("wrong_dim"):
    client.delete_collection("wrong_dim")
client.create_collection(
    collection_name="wrong_dim",
    vectors_config=VectorParams(size=10, distance=Distance.COSINE),
)

v1 = emb.embed_query("데이터 파이프라인을 매일 실행합니다")
try:
    client.upsert(
        collection_name="wrong_dim",
        points=[PointStruct(id=1, vector=v1, payload={"text": "x"})],
    )
except Exception as e:
    print(type(e).__name__)
    print(str(e)[:300])

client.delete_collection("wrong_dim")
