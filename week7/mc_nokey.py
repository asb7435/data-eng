# mc_nokey.py — 없는 키 · 실제 키 목록
from minio_env import mc, BUCKET

try:
    mc.get_object(BUCKET, "notes/없는파일.txt")
except Exception as e:
    print(type(e).__name__, "-", getattr(e, "code", ""))

keys = [o.object_name for o in mc.list_objects(BUCKET, recursive=True)]
print(keys)
