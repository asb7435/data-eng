# emb_table.py — 문장 5개끼리의 유사도 표
from rag_env import get_emb

emb = get_emb()
def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb)

sents = [
    "ETL은 추출, 변환, 적재 순서로 데이터를 옮깁니다",
    "ELT는 먼저 적재하고 나중에 변환합니다",
    "Airflow는 작업 순서를 관리하는 도구입니다",
    "Kafka는 이벤트를 실시간으로 흘려보냅니다",
    "오늘 날씨가 참 좋습니다",
]
vecs = emb.embed_documents(sents)

print("      ", "  ".join(f"{i:5}" for i in range(len(sents))))
for i, a in enumerate(vecs):
    row = "  ".join(f"{cos(a, b):5.2f}" for b in vecs)
    print(f"{i:5} ", row)

for i, s in enumerate(sents):
    print(i, s)
