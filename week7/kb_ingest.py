# kb_ingest.py — 버킷 전체를 lecture_kb 에 적재
from kb import ingest, client, COLLECTION

print("적재:", ingest())
print("총 포인트:", client.count(COLLECTION))
