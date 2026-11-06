# producer_noflush.py — 일부러 flush를 뺐습니다
import json
from confluent_kafka import Producer

p = Producer({"bootstrap.servers": "localhost:9092"})
for i in range(1000):
    p.produce("orders-test", value=json.dumps({"i": i}))
print("보냈다고 생각한 건수: 1000")
# flush() 없음 — 여기서 프로그램이 끝납니다
p.flush()
