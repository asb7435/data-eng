# history.py — 앞 대화를 목록으로 함께 보냅니다
from langchain_core.messages import SystemMessage, HumanMessage
from rag_env import llm

history = [
    SystemMessage(content="너는 친절한 조교야. 한국어로 짧게 답해줘."),
    HumanMessage(content="내 이름은 홍길동이야"),
]
ans1 = llm.invoke(history)
print("봇:", ans1.content)

history.append(ans1)
history.append(HumanMessage(content="내 이름이 뭐라고 했지?"))
ans2 = llm.invoke(history)
print("봇:", ans2.content)
