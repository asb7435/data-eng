# emb_batch.py — 하나씩 부르기 vs 한꺼번에 부르기
import time
from rag_env import get_emb

emb = get_emb()
sents = ["ETL은 추출, 변환, 적재 순서로 데이터를 옮깁니다", "ELT는 먼저 적재하고 나중에 변환합니다",
         "Airflow는 작업 순서를 관리하는 도구입니다", "Kafka는 이벤트를 실시간으로 흘려보냅니다",
         "오늘 날씨가 참 좋습니다"]
emb.embed_query("준비")   # 모델을 메모리에 올려 두고 잽니다

t0 = time.time()
for s in sents:
    emb.embed_query(s)
one_by_one = time.time() - t0

t0 = time.time()
emb.embed_documents(sents)
batched = time.time() - t0

print(f"하나씩: {one_by_one:.2f}초 / 배치: {batched:.2f}초")
