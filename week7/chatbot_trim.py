# chatbot_trim.py — 시스템 메시지는 지키고 최근 N개만 보냅니다
from langchain_core.messages import SystemMessage, HumanMessage
from rag_env import llm

MAX_MSGS = 4   # 시스템 메시지를 뺀 최근 메시지 수(질문 · 답 두 쌍)

def trim(history, max_msgs=MAX_MSGS):
    if len(history) <= max_msgs + 1:
        return history
    return [history[0]] + history[-max_msgs:]

history = [SystemMessage(content="너는 친절한 조교야. 한국어로 짧게 답해줘.")]

while True:
    q = input("나: ")
    if q.strip() in ("quit", "exit"):
        break
    history.append(HumanMessage(content=q))
    history = trim(history)
    sent = len(history) - 1          # 이번에 보내는 메시지 수(시스템 메시지 제외)
    answer = llm.invoke(history)
    history.append(answer)
    print("봇:", answer.content)
    print(f"   (보낸 이력 {sent}개 · 입력 토큰 {answer.usage_metadata['input_tokens']})")
