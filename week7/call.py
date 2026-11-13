# call.py — 첫 호출
from rag_env import llm

resp = llm.invoke("데이터 엔지니어링을 한 문장으로 소개해줘")
print(resp.content)

# 응답 객체를 들여다봅니다
print(type(resp))
print(resp.usage_metadata)   # 입력 · 출력 토큰 수 — OpenAI · Ollama 공통
