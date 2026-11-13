# split.py — 200자 조각으로 자릅니다
from langchain_community.document_loaders import TextLoader

docs = TextLoader("notes.txt", encoding="utf-8").load()
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,        # 한 조각 최대 200자
    chunk_overlap=30,      # 이웃 조각과 30자 겹침
    separators=["\n\n", "\n", " ", ""],   # 문단 → 줄 → 공백 → 글자 순으로 시도
)
chunks = splitter.split_documents(docs)
print("조각 수:", len(chunks))
for i, c in enumerate(chunks):
    print(f"--- chunk {i} ({len(c.page_content)}자) ---")
    print(c.page_content)
