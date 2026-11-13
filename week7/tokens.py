# tokens.py — 턴이 늘수록 보내는 토큰이 커지는 것을 봅니다
from langchain_core.messages import SystemMessage, HumanMessage
from rag_env import llm

h = [SystemMessage(content="한 문장으로 짧게 답해줘.")]
for i in range(5):
    h.append(HumanMessage(content=f"{i}번째 질문이야. 아무 말이나 한 줄 해줘."))
    a = llm.invoke(h)
    h.append(a)
    print(f"{i+1}턴 — 입력 토큰 {a.usage_metadata['input_tokens']} / 이력 {len(h)}개")
