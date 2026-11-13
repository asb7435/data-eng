# load.py — 파일 하나를 Document 하나로
from langchain_community.document_loaders import TextLoader

docs = TextLoader("notes.txt", encoding="utf-8").load()
print(len(docs))                    # 파일 1개 = Document 1개
print(docs[0].metadata)             # {'source': 'notes.txt'}
print(docs[0].page_content[:80])

# PDF는 페이지당 Document 1개로 로드됩니다
# from langchain_community.document_loaders import PyPDFLoader
# docs = PyPDFLoader("sample.pdf").load()
