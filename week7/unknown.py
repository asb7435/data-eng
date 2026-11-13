# unknown.py — 모델이 알 수 없는 질문
from rag_env import llm

q = "우리 회사의 2026년 3분기 데이터 파이프라인 장애 건수는 몇 건이야?"
print(llm.invoke(q).content)
