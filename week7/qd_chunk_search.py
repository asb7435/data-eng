# qd_chunk_search.py — 질문에 걸린 조각과 출처
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from rag_env import get_emb

emb = get_emb()
client = QdrantClient(url="http://localhost:6333")

hits = client.query_points(
    collection_name="my_notes",
    query=emb.embed_query("배치와 스트리밍은 어떻게 다른가요?"),
    limit=3,
).points

for h in hits:
    print(f"--- {h.score:.3f} (출처: {h.payload.get('source')}) ---")
    print(h.payload["text"][:120])
    print()
