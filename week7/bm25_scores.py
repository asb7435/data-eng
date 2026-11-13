# bm25_scores.py — 「Airflow」 한 낱말의 점수
from kb_corpus import bm25, corpus

q = "Airflow"
scores = bm25.get_scores(q.split())
order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
for i in order[:5]:
    print(f"{scores[i]:6.2f}  {corpus[i][:40].replace(chr(10), ' ')}")
