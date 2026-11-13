# md_split.py — 제목(##) 경계를 먼저 쓰는 분할기와 비교
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

md = """# 데이터 엔지니어링

## 1. 수집

크롤러와 CDC로 원천에서 데이터를 가져옵니다.
API는 호출 한도를 지킵니다.

## 2. 저장

오브젝트 스토리지 위에 레이크하우스를 올립니다.

## 3. 처리

Spark로 분산 처리합니다.
"""
with open("doc.md", "w", encoding="utf-8") as f:
    f.write(md)
docs_md = TextLoader("doc.md", encoding="utf-8").load()

# 기본 분할기
a = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=0)
# 제목 경계를 우선하는 분할기
b = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=0,
                                   separators=["\n## ", "\n\n", "\n", " ", ""])

for name, sp in [("기본", a), ("제목 우선", b)]:
    cs = sp.split_documents(docs_md)
    print(f"--- {name}: {len(cs)}개 ---")
    for c in cs:
        print("  |", c.page_content.replace("\n", " "))
