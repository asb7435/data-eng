# kb_shrink.py — long_notes.txt 를 한 줄짜리로 바꿔 다시 적재
from kb import ingest, count_of
from minio_env import mc, BUCKET

SRC = f"minio://{BUCKET}/notes/long_notes.txt"
print("변경 전:", count_of(SRC))

with open("short.txt", "w", encoding="utf-8") as f:
    f.write("데이터 파이프라인 요약본입니다.\n")
mc.fput_object(BUCKET, "notes/long_notes.txt", "short.txt")   # 같은 키에 짧은 글을 덮어씀

ingest(prefix="notes/long_notes.txt")
print("변경 후:", count_of(SRC), "← 줄어들지 않았습니다")
