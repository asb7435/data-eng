# enc.py — 일부러 틀린 인코딩으로 읽어 봅니다
from langchain_community.document_loaders import TextLoader

try:
    TextLoader("notes.txt", encoding="cp949").load()
except Exception as e:
    print(type(e).__name__, "-", e)
    print("원인:", type(e.__cause__).__name__, "-", e.__cause__)
