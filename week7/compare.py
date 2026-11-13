# compare.py — 구분자 하나만 쓰는 단순 분할기와 비교
from langchain_community.document_loaders import TextLoader

docs = TextLoader("notes.txt", encoding="utf-8").load()
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,        # 한 조각 최대 200자
    chunk_overlap=30,      # 이웃 조각과 30자 겹침
    separators=["\n\n", "\n", " ", ""],   # 문단 → 줄 → 공백 → 글자 순으로 시도
)
chunks = splitter.split_documents(docs)
from langchain_text_splitters import CharacterTextSplitter

simple = CharacterTextSplitter(separator="\n\n", chunk_size=200, chunk_overlap=30)
simple_chunks = simple.split_documents(docs)

print("Recursive:", [len(c.page_content) for c in chunks])
print("Character:", [len(c.page_content) for c in simple_chunks])
