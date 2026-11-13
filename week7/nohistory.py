# nohistory.py — 두 번을 따로 부릅니다
from rag_env import llm

print(llm.invoke("내 이름은 홍길동이야").content)
print("---")
print(llm.invoke("내 이름이 뭐라고 했지?").content)
