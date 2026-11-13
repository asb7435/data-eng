# overlap.py — 이웃 조각의 끝과 시작을 나란히 봅니다
from langchain_community.document_loaders import TextLoader

docs = TextLoader("notes.txt", encoding="utf-8").load()
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,        # 한 조각 최대 200자
    chunk_overlap=30,      # 이웃 조각과 30자 겹침
    separators=["\n\n", "\n", " ", ""],   # 문단 → 줄 → 공백 → 글자 순으로 시도
)
chunks = splitter.split_documents(docs)
for i in range(len(chunks) - 1):
    tail = chunks[i].page_content[-40:]
    head = chunks[i + 1].page_content[:40]
    print(f"[{i}] 끝  : ...{tail!r}")
    print(f"[{i+1}] 시작: {head!r}...")
    print()
