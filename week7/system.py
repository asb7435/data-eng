# system.py — 같은 질문, 다른 역할
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag_env import llm

def ask(system_text, question):
    p = ChatPromptTemplate.from_messages([("system", system_text), ("human", "{q}")])
    return (p | llm | StrOutputParser()).invoke({"q": question})

q = "Kafka가 뭐야?"
print("[초등학생에게]", ask("초등학생도 이해할 수 있게 비유로 두 문장 안에 설명해줘.", q))
print()
print("[면접관에게]", ask("면접 답변처럼 기술 용어를 써서 3문장으로 답해줘.", q))
