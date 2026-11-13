# emb_cos.py — 코사인 유사도를 직접 계산합니다
from rag_env import get_emb

emb = get_emb()
v1 = emb.embed_query("데이터 파이프라인을 매일 실행합니다")
v2 = emb.embed_query("배치 작업을 하루에 한 번 돌립니다")
v3 = emb.embed_query("오늘 점심은 김치찌개입니다")

def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb)

print("비슷한 문장:", round(cos(v1, v2), 3))
print("다른 문장:  ", round(cos(v1, v3), 3))
