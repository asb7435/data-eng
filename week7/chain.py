# chain.py — prompt | llm | parser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag_env import llm

prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 데이터 엔지니어링 강의의 조교야. 한국어로 짧고 정확하게 답해줘."),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()
print(chain.invoke({"question": "ETL과 ELT의 차이를 설명해줘"}))

# 파서를 빼면 무엇이 나오는지 비교
chain_no_parser = prompt | llm
r1 = chain_no_parser.invoke({"question": "테스트"})
r2 = chain.invoke({"question": "테스트"})
print(type(r1).__name__)               # AIMessage
print(isinstance(r2, str), r2[:20])    # True — 글자(str)로 나온다
