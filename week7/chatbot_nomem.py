# chatbot_nomem.py — 이력을 보내지 않는 판(비교용)
from langchain_core.messages import SystemMessage, HumanMessage
from rag_env import llm

system = SystemMessage(content="너는 친절한 데이터 엔지니어링 학습 조교야. 한국어로 짧게 답해줘.")

while True:
    q = input("나: ")
    if q.strip() in ("quit", "exit"):
        break
    answer = llm.invoke([system, HumanMessage(content=q)])   # 시스템 메시지 + 이번 질문만
    print("봇:", answer.content)
