import json
from pathlib import Path

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)

from rag_env import llm

MAX_MSGS = 2
HISTORY_PATH = Path(__file__).with_name("chat_history.json")

SYSTEM = SystemMessage(
    content=(
        "너는 친절한 조교야. 한국어로 짧게 답해줘. "
        "사용자의 이름을 다시 말하지 마. "
        "모르는 것은 추측하지 말고 모른다고 답해."
    )
)

if HISTORY_PATH.exists():
    history = messages_from_dict(
        json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    )
    print(f"저장된 대화 {len(history)}개를 불러왔습니다.")
else:
    history = []

while True:
    q = input("나: ").strip()
    if q.lower() in ("quit", "exit"):
        break
    if not q:
        continue

    user_msg = HumanMessage(content=q)

    # 방금 입력한 질문을 포함해 최근 2개만 모델에 보냅니다.
    recent = (history + [user_msg])[-MAX_MSGS:]
    answer = llm.invoke([SYSTEM] + recent)

    # 파일에는 전체 대화를 저장합니다.
    history.extend([user_msg, answer])
    HISTORY_PATH.write_text(
        json.dumps(messages_to_dict(history), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("봇:", answer.content)
    print(f"   (보낸 이력 {len(recent)}개 · 저장된 이력 {len(history)}개)")
