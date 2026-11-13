# emb_dim.py — 문장 하나를 벡터로
from rag_env import PROVIDER, get_emb

emb = get_emb()
v1 = emb.embed_query("데이터 파이프라인을 매일 실행합니다")
print(PROVIDER, "차원:", len(v1))
print("앞 5개 값:", [round(x, 4) for x in v1[:5]])
