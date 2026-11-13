# temp.py — 같은 질문을 temperature 0 과 1.0 으로 세 번씩
from rag_env import get_llm

for t in [0, 1.0]:
    m = get_llm(temperature=t)
    print(f"--- temperature={t} ---")
    for i in range(3):
        print(" ", m.invoke("데이터 파이프라인을 한 문장으로").content[:60])
