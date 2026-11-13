# show.py — 같은 질문에 두 검색기가 고른 조각
from kb_corpus import short
from retrievers import bm25_rank, vector_rank

def show(query):
    print(f"\n=== {query} ===")
    b = bm25_rank(query, 2)
    v = vector_rank(query, 2)
    print("  BM25  :", [short(i) for i in b] or "없음")
    print("  Vector:", [short(i) for i in v])

if __name__ == "__main__":
    show("Airflow")                      # 고유명사 — 조사 없이 쓴 곳만
    show("일정을 정해 두고 도는 작업")      # 풀어 쓴 질문
    show("Kafka 파티션")                  # 문서에는 「파티션으로」「파티션에」
    show("ERR-4021")                     # 장애 코드
