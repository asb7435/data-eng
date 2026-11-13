# qd_search.py — 질문과 가까운 문장 셋
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from rag_env import get_emb

emb = get_emb()
client = QdrantClient(url="http://localhost:6333")

COLLECTION = "lecture_notes"

def search(q, limit=3, flt=None):
    hits = client.query_points(
        collection_name=COLLECTION,
        query=emb.embed_query(q),
        limit=limit,
        query_filter=flt,
    ).points
    print(f"\nQ: {q}")
    for h in hits:
        print(f"  {h.score:.3f}  [{h.payload['category']}] {h.payload['text']}")

if __name__ == "__main__":
    search("작업 순서를 관리하는 도구는?")
    search("실시간으로 데이터가 흘러가게 하려면?")
    search("데이터를 먼저 넣고 나중에 손보는 방식")
