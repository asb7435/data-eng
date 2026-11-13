# meta.py — 조각마다 metadata 가 따라오는지, 직접 더할 수 있는지
from langchain_community.document_loaders import TextLoader

docs = TextLoader("notes.txt", encoding="utf-8").load()
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,        # 한 조각 최대 200자
    chunk_overlap=30,      # 이웃 조각과 30자 겹침
    separators=["\n\n", "\n", " ", ""],   # 문단 → 줄 → 공백 → 글자 순으로 시도
)
chunks = splitter.split_documents(docs)
for i, c in enumerate(chunks):
    print(i, c.metadata)

# 메타데이터를 직접 추가할 수도 있습니다
for i, c in enumerate(chunks):
    c.metadata["chunk_id"] = i
    c.metadata["chars"] = len(c.page_content)
print(chunks[0].metadata)
