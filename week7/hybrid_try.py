# hybrid_try.py — 두 순위와 합친 순위를 나란히
from kb_corpus import short
from retrievers import bm25_rank, vector_rank
from hybrid import hybrid_ids

q = "작업 순서를 관리하는 도구는?"
for name, r in [("BM25", bm25_rank(q, 3)), ("벡터", vector_rank(q, 3)), ("하이브리드", hybrid_ids(q, 3))]:
    print(f"{name:6}", [short(i, 16) for i in r])
