# kb_rebuild.py — 원본을 다시 올리고 컬렉션째 새로 색인
from kb import ingest, client, COLLECTION
from minio_env import mc, BUCKET

mc.fput_object(BUCKET, "notes/long_notes.txt", "long_notes.txt")   # 5단계에서 줄인 원본을 되돌림

client.delete_collection(COLLECTION)
print("재색인:", ingest())
print("총 포인트:", client.count(COLLECTION))
