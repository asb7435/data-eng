# kw_hits.py — "CDC" 가 든 조각을 크기별로
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = TextLoader("long_notes.txt", encoding="utf-8").load()

keyword = "CDC"
for size in [100, 1000]:
    s = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=size // 10)
    cs = s.split_documents(docs)
    hits = [c for c in cs if keyword in c.page_content]
    print(f"\n=== chunk_size={size} — {len(hits)}개 조각에서 발견, 그 조각 {len(hits[0].page_content)}자 ===")
    print(hits[0].page_content[:300])
