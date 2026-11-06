# consumer_manual.py — 처리 성공 후에만 커밋
import json
from confluent_kafka import Consumer

c = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "order-manual",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,      # 자동 커밋 끄기
})
c.subscribe(["orders"])

def handle(order):
    # 일부러 실패시켜 보기: amount가 5의 배수면 예외
    if order["amount"] % 5 == 0:
        raise ValueError(f"처리 실패: {order['order_id']}")
    print(f"처리 완료: {order}")

try:
    while True:
        msg = c.poll(1.0)
        if msg is None or msg.error():
            continue
        order = json.loads(msg.value().decode("utf-8"))
        try:
            handle(order)
            c.commit(msg)            # 성공했을 때만 커밋
        except ValueError as e:
            print(f"{e} — 커밋하지 않고 멈춥니다 (다시 켜면 이 메시지부터)")
            break                    # 건너뛰고 다음 것을 커밋하면 이것까지 덮인다
except KeyboardInterrupt:
    pass
finally:
    c.close()
