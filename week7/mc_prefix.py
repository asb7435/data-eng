# mc_prefix.py — manual/ 에 한 문서를 더 올리고 접두사로 훑습니다
from minio_env import mc, BUCKET

mc.fput_object(BUCKET, "manual/guide.txt", "guide.txt")

print("전체:")
for o in mc.list_objects(BUCKET, recursive=True):
    print("  ", o.object_name)

print("notes/ 만:")
for o in mc.list_objects(BUCKET, prefix="notes/", recursive=True):
    print("  ", o.object_name)
