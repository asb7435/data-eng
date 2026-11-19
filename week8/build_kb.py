"""MinIO 문서를 Qdrant에 재색인하는 실행 스크립트."""

import os
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models

from minio_env import mc, read_text
from rag_env import get_emb


BUCKET = os.getenv("BUCKET", "raw-docs")
COLLECTION = os.getenv("COLLECTION", "lecture_kb")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))

emb = get_emb()

qc = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333")
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_SIZE // 10,
)


def prepare_collection():
    dimension = len(emb.embed_query("차원 확인"))

    if qc.collection_exists(COLLECTION):
        config = qc.get_collection(COLLECTION)
        existing_dim = config.config.params.vectors.size

        if existing_dim != dimension:
            raise ValueError(
                f"벡터 차원 불일치: "
                f"컬렉션={existing_dim}, 모델={dimension}"
            )
    else:
        qc.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=dimension,
                distance=models.Distance.COSINE,
            ),
        )


def ingest_document(key):
    source = f"minio://{BUCKET}/{key}"
    content = read_text(BUCKET, key)
    chunks = splitter.split_text(content)

    vectors = emb.embed_documents(chunks) if chunks else []

    # 같은 문서의 과거 청크를 제거
    qc.delete(
        collection_name=COLLECTION,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="source",
                        match=models.MatchValue(value=source),
                    )
                ]
            )
        ),
        wait=True,
    )

    if not chunks:
        return 0

    points = []

    for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
        point_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"{source}#{index}",
            )
        )

        points.append(
            models.PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "text": chunk,
                    "source": source,
                    "chunk_index": index,
                },
            )
        )

    qc.upsert(
        collection_name=COLLECTION,
        points=points,
        wait=True,
    )

    return len(points)


def main():
    prepare_collection()

    total = 0

    for obj in mc.list_objects(BUCKET, recursive=True):
        if not obj.object_name.endswith(".txt"):
            continue

        count = ingest_document(obj.object_name)
        total += count

        print(f"{obj.object_name} → {count} chunks")

    stored = qc.count(
        collection_name=COLLECTION,
        exact=True,
    ).count

    print(f"적재 {total} 조각 · 총 {stored}")


if __name__ == "__main__":
    main()
