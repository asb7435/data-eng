# template.py — 보낼 메시지의 틀(아직 모델을 부르지 않습니다)
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 데이터 엔지니어링 강의의 조교야. 한국어로 짧고 정확하게 답해줘."),
    ("human", "{question}"),
])

print(prompt.invoke({"question": "ETL과 ELT의 차이를 설명해줘"}))
