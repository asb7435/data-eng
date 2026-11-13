# mc_read.py — 올린 문서를 다시 읽어 옵니다(read_text 는 minio_env.py 에)
from minio_env import BUCKET, read_text

text = read_text(BUCKET, "notes/notes.txt")
print(len(text), "자")
print(text[:100])
