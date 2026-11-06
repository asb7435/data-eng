# consumer_test.py
import json
from collections import defaultdict
from confluent_kafka import Consumer
import sqlite3
from pathlib import Path

c = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "order-agg",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False, #db 저장 성공한 뒤 직접 오프셋을 커밋
    "enable.auto.offset.store": False,
})


def on_assign(consumer, partitions):
    print(
        f"할당된 파티션: {[p.partition for p in partitions]}",
        flush=True,
    )

def on_revoke(consumer, partitions):
    print(
        f"반납한 파티션: {[p.partition for p in partitions]}",
        flush=True,
    )

c.subscribe(
    ["orders"],
    on_assign=on_assign,
    on_revoke=on_revoke,
)

# consumer_test.py와 같은 폴더에 DB 파일을 만듭니다.
db_path = Path(__file__).resolve().with_name("orders.db")
db = sqlite3.connect(str(db_path), timeout=30)

# 두 Consumer가 같은 DB를 사용하도록 설정합니다.
db.execute("PRAGMA journal_mode=WAL")

db.executescript("""
CREATE TABLE IF NOT EXISTS totals (
    customer TEXT PRIMARY KEY,
    amount INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS processed (
    topic TEXT NOT NULL,
    partition_id INTEGER NOT NULL,
    offset_id INTEGER NOT NULL,
    PRIMARY KEY (topic, partition_id, offset_id)
);
""")
db.commit()


try:
    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"오류: {msg.error()}")
            continue
# 
        order = json.loads(msg.value().decode("utf-8"))
	# 처리 기록과 누적 금액을 함께 저장, 이미 처리한 메시지라면 금액 다시 더하지 않음
        with db:
            inserted = db.execute(
                """
                INSERT OR IGNORE INTO processed
                (topic, partition_id, offset_id)
                VALUES (?, ?, ?)
                """,
                (msg.topic(), msg.partition(), msg.offset()),
            ).rowcount

            if inserted:
                db.execute(
                    """
                    INSERT INTO totals (customer, amount)
                    VALUES (?, ?)
                    ON CONFLICT(customer)
                    DO UPDATE SET amount = totals.amount + excluded.amount
                    """,
                    (order["customer"], order["amount"]),
                )

        # DB 저장 성공 후 Kafka 오프셋을 커밋합니다.
        c.commit(message=msg, asynchronous=False)

        saved_totals = dict(
            db.execute("SELECT customer, amount FROM totals")
        )

        print(
            f"[p{msg.partition()}:{msg.offset()}] "
            f"{'신규 저장' if inserted else '중복 제외'} "
            f"| 누적 {saved_totals}",
            flush=True,
        )
except KeyboardInterrupt:
    pass
finally:
    c.close()
    db.close()           # 그룹에서 정상 탈퇴 + 오프셋 정리
