# qd_filter.py — category 가 "도구" 인 것만
from qdrant_client.models import Filter, FieldCondition, MatchValue
from qd_search import search

only_tools = Filter(
    must=[FieldCondition(key="category", match=MatchValue(value="도구"))]
)

search("데이터를 옮기는 방법", limit=3)                 # 필터 없음
search("데이터를 옮기는 방법", limit=3, flt=only_tools)  # 도구만
