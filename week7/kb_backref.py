# kb_backref.py — 찾은 조각의 source 로 원본 전체를 다시 읽습니다
from kb import client, emb, COLLECTION
from minio_env import read_text

hits = client.query_points(
    collection_name=COLLECTION,
    query=emb.embed_query("작업 순서를 관리하는 도구는?"),
    limit=1,
).points

top = hits[0]
print("검색된 chunk:", top.payload["text"][:60])
print("출처:", top.payload["source"])

_, _, rest = top.payload["source"].partition("minio://")
bucket, _, key = rest.partition("/")
print("원본 전체:", read_text(bucket, key)[:120])
