# mc_upload.py — 버킷을 만들고 7-2 에서 만든 문서 둘을 올립니다
from minio_env import mc, BUCKET

if not mc.bucket_exists(BUCKET):
    mc.make_bucket(BUCKET)

mc.fput_object(BUCKET, "notes/notes.txt", "notes.txt")
mc.fput_object(BUCKET, "notes/long_notes.txt", "long_notes.txt")

for obj in mc.list_objects(BUCKET, recursive=True):
    print(obj.object_name, obj.size, "bytes")
