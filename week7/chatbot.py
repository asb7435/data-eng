# chatbot.py — 이력을 쌓아 가는 콘솔 챗봇
from langchain_core.messages import SystemMessage, HumanMessage
from rag_env import llm

history = [SystemMessage(content="너는 친절한 데이터 엔지니어링 학습 조교야. 한국어로 짧게 답해줘.")]

while True:
    q = input("나: ")
    if q.strip() in ("quit", "exit"):
        break
    history.append(HumanMessage(content=q))
    answer = llm.invoke(history)     # 지금까지의 대화 전체를 보낸다
    history.append(answer)           # AIMessage를 이력에 추가
    print("봇:", answer.content)
    print(f"   (이력 {len(history)}개 메시지)")
