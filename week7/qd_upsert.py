# qd_upsert.py — 문장 6개를 payload 와 함께 넣습니다
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from rag_env import get_emb

emb = get_emb()
client = QdrantClient(url="http://localhost:6333")

COLLECTION = "lecture_notes"
texts = [
    "ETL은 추출, 변환, 적재 순서로 데이터를 옮기는 방식입니다",
    "ELT는 먼저 적재한 뒤 저장소 안에서 변환합니다",
    "Airflow는 워크플로 오케스트레이션 도구입니다",
    "Kafka는 이벤트 스트리밍 플랫폼입니다",
    "Iceberg는 오브젝트 스토리지 위의 테이블 형식입니다",
    "Spark는 대용량 데이터를 분산 처리합니다",
]
cats = ["개념", "개념", "도구", "도구", "저장", "처리"]

vectors = emb.embed_documents(texts)          # 배치로 한 번에
points = [
    PointStruct(id=i, vector=vec,
                payload={"text": t, "category": c, "source": "lecture"})
    for i, (t, vec, c) in enumerate(zip(texts, vectors, cats))
]
client.upsert(collection_name=COLLECTION, points=points)
print(client.count(COLLECTION))
