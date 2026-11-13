# kb_reingest.py — 그 문서의 옛 조각을 지우고 다시 넣기
from kb import reingest, count_of
from minio_env import BUCKET

SRC = f"minio://{BUCKET}/notes/long_notes.txt"
print("재적재:", reingest("notes/long_notes.txt"))
print("최종:", count_of(SRC), "← 줄어들었습니다")
