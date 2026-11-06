# WEEK6 DAY3 MINI

## 1. Consumer 두 개로 파티션 나눠 처리하기

### 실행 방법

Consumer 두 개의 `group.id`를 모두 `order-agg`로 설정했다. 기존 코드는 메시지를 받았을 때만 출력하기 때문에, 메시지가 없는 파티션을 맡으면 정상적으로 할당됐는지 알기 어려웠다. 이를 확인하려고 파티션 할당과 반납 시점을 출력하는 콜백을 추가했다.

```python
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
```

터미널 두 개에서 각각 다음 명령을 실행하고, 다른 터미널에서 Producer를 실행했다.

```bash
# 터미널 1과 2에서 각각 실행
python -u consumer_test.py

# 터미널 3에서 실행
python producer_test.py
```

### 확인한 결과

두 Consumer의 최종 할당과 메시지 출력은 다음과 같았다.

| 구분 | 할당된 파티션 | 처리한 고객 |
|---|---|---|
| Consumer 1 | `[2]` | `user2`, `user3` |
| Consumer 2 | `[0, 1]` | `user1` |

실제 출력에서도 Consumer 1에는 `p2`, Consumer 2에는 `p1`이 표시됐다.

```text
# Consumer 1
[p2:126] {'order_id': 1, 'customer': 'user2', 'amount': 5644} | 누적 {'user3': 321201, 'user2': 249934}
[p2:128] {'order_id': 4, 'customer': 'user3', 'amount': 27793} | 누적 {'user3': 348994, 'user2': 254221}

# Consumer 2
[p1:56] {'order_id': 5, 'customer': 'user1', 'amount': 21568} | 누적 {'user1': 201958}
[p1:57] {'order_id': 6, 'customer': 'user1', 'amount': 2324} | 누적 {'user1': 204282}
```

실행 중 파티션을 반납했다가 다시 할당받는 출력도 나타났다. Consumer가 그룹에 참여하거나 종료되면서 파티션을 다시 분배하는 리밸런싱이 일어났다.


Producer는 고객 ID를 메시지 키로 사용했다. 현재 설정과 파티션 수에서는 `user1`이 1번으로, `user2`와 `user3`가 2번으로 전송돼 0번에는 메시지가 들어가지 않았다.

파티션이 세 개라고 해서 메시지가 반드시 세 곳에 골고루 들어가는 것은 아니다. 같은 키는 해시 결과에 따라 같은 파티션으로 전송된다. 따라서 빈 0번만 할당받은 Consumer는 정상 실행 중이어도 읽을 메시지가 없어 주문 출력이 나오지 않을 수 있다.

`[0, 1]`을 맡은 Consumer가 1번의 메시지를 처리했으므로 완전히 조용하지는 않았다. 0번만 맡는 경우는 직접 관찰한 결과가 아니라, 빈 파티션의 동작으로 설명할 수 있는 경우다.

## 2. acks 설정 추가 전후의 전송 지연 비교

### 설정과 측정 방법

기존 Producer 설정과 `"acks": "all"`을 추가한 설정에서 delivery report의 전송 지연을 비교했다. 다른 측정 조건은 유지하고 `acks` 설정의 명시 여부만 바꿨다.

```python
# 추가 전
p = Producer({
    "bootstrap.servers": "localhost:9092",
})

# 추가 후
p = Producer({
    "bootstrap.servers": "localhost:9092",
    "acks": "all",
})
```

Delivery report에서는 `msg.latency()`를 이용해 전송 지연을 밀리초 단위로 출력했다.

```python
def on_delivery(err, msg):
    if err is not None:
        print(f"전송 실패: {err}")
    else:
        print(
            f"전송 완료 partition={msg.partition()} "
            f"offset={msg.offset()} "
            f"전송 지연={msg.latency() * 1000:.2f}ms"
        )
```

기존의 `time.sleep(1)` 대신 다음 코드를 사용해, 다음 주문을 기다리는 동안에도 콜백을 처리하도록 했다. 두 설정 모두 같은 측정 코드를 사용했다.

```python
until = time.perf_counter() + 1
while time.perf_counter() < until:
    p.poll(0.01)
```

### 측정 결과

화면에서 확인한 출력 중 설정 생략 상태의 6건과 `all`을 명시한 상태의 7건을 비교했다. 전체 30건의 평균은 아니다. 실제 측정은 `all`을 명시한 실행을 먼저 하고, 이후 설정을 생략해 실행했다.

| 설정 | 측정한 전송 지연(ms) | 평균 |
|---|---|---:|
| `acks` 생략 | 6.11, 6.57, 6.47, 7.14, 6.94, 6.32 | 약 6.59ms |
| `acks="all"` 명시 | 6.41, 7.64, 6.85, 7.87, 7.89, 8.14, 6.28 | 약 7.30ms |

`all`을 명시한 실행의 평균 지연이 약 **0.71ms** 높게 나왔다. 다만 표본 수가 적고 서로 다른 시점에 측정했으므로, 이 차이가 설정을 추가해서 발생했다고 보기는 어렵다.

사용한 confluent-kafka의 기반 라이브러리인 librdkafka는 기본 `acks` 값이 이미 `all`이다. 따라서 별도로 다른 설정을 주지 않았다면 `acks`를 생략한 경우와 `"all"`을 명시한 경우의 확인 조건은 같다. 이번 결과는 설정 추가에 따른 뚜렷한 속도 변화보다는 실행 시점에 따른 지연 변동으로 해석하는 것이 적절하다.

`acks="all"`은 현재 동기화된 복제본인 ISR의 확인을 기다린다는 뜻이다. 수업에서 안내한 단일 브로커·복제 계수 1 환경에서는 추가 복제본의 확인을 기다리는 과정도 없다.

공식 설정 설명: [librdkafka Configuration properties](https://docs.confluent.io/platform/current/clients/librdkafka/html/md_CONFIGURATION.html)

## 3. 집계 결과를 SQLite에 저장하기

### 저장 방식

기존 코드는 고객별 누적 금액을 `defaultdict`에만 저장했다. 이 값은 프로그램 메모리에 있으므로 Consumer를 종료하면 사라진다. Kafka 오프셋이 남아 있어도 집계 금액까지 복원되는 것은 아니다.

`consumer_test.py`와 같은 폴더에 `orders.db`를 만들고, 두 테이블을 사용했다.

| 테이블 | 저장 내용 |
|---|---|
| `totals` | 고객별 누적 주문 금액 |
| `processed` | 처리한 메시지의 토픽, 파티션, 오프셋 |

```sql
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
```

두 Consumer가 같은 DB를 사용할 수 있도록 WAL 모드와 연결 대기 시간을 설정했다. 각 프로세스는 자신의 SQLite 연결을 사용한다.

```python
db_path = Path(__file__).resolve().with_name("orders.db")
db = sqlite3.connect(str(db_path), timeout=30)
db.execute("PRAGMA journal_mode=WAL")
```

### 저장과 커밋 순서

Consumer의 자동 커밋을 끄고 다음 순서로 처리했다.

1. `processed` 테이블에 메시지 처리 기록을 추가한다.
2. 처음 처리하는 메시지라면 고객별 누적 금액을 갱신한다.
3. 처리 기록과 누적 금액을 하나의 SQLite 트랜잭션으로 저장한다.
4. DB 저장이 성공한 뒤 Kafka 오프셋을 수동 커밋한다.

```python
"enable.auto.commit": False,
"enable.auto.offset.store": False,
```

```python
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

c.commit(message=msg, asynchronous=False)
```

DB 저장 직후 Kafka 오프셋을 커밋하기 전에 Consumer가 종료되면, 재시작 후 같은 메시지를 다시 받을 수 있다. 이때 `processed`의 기본 키 제약으로 이미 처리한 메시지를 구분하고, 누적 금액에는 다시 더하지 않도록 했다.

이 방식은 같은 Kafka 메시지의 재처리에 따른 중복 집계를 막는다. 같은 주문을 새로운 메시지로 다시 발행하는 경우까지 구분하려면 별도의 고유 주문 ID가 필요하다.

### 재시작 전후 확인

Consumer를 종료하기 전과 재시작해 새 주문을 처리한 뒤, 다음 명령으로 DB를 조회했다.

```bash
python -c "import sqlite3; c=sqlite3.connect('orders.db'); print(dict(c.execute('SELECT customer, amount FROM totals'))); c.close()"
```

| 고객 | 재시작 전 | 재시작 후 | 증가액 |
|---|---:|---:|---:|
| user1 | 233,989 | 356,780 | 122,791 |
| user3 | 308,472 | 547,261 | 238,789 |
| user2 | 226,757 | 667,145 | 440,388 |

재시작 후 첫 메시지의 출력은 다음과 같았다.

```text
[p2:204] 신규 저장 | 누적 {'user1': 233989, 'user3': 308472, 'user2': 240895}
```

`user1`과 `user3`의 금액은 재시작 전 값이 그대로 유지됐고, `user2`는 기존 226,757원에 새 주문 금액 14,138원이 더해져 240,895원이 됐다. 누적 금액이 0부터 시작하지 않고 기존 값에서 이어진 것을 확인했다.

### 재시작해도 누적을 이어가려면

Consumer를 껐다 켜도 누적을 이어가려면, 이전에 계산한 집계값을 프로그램 밖에 저장해야 한다. 이번 실습에서는 그 저장소로 SQLite를 사용했다. Kafka 오프셋은 어디까지 읽었는지를 기록하고, SQLite는 지금까지 얼마를 집계했는지를 보관한다. 두 정보의 역할이 다르므로 함께 관리해야 한다.

- `orders.db`를 유지해야 이전에 집계한 금액이 남는다.
- 같은 `group.id`와 커밋된 오프셋을 사용해야 이어서 읽을 수 있다.
- DB 저장 후 오프셋을 커밋해야 저장하지 못한 메시지를 건너뛰지 않는다.
- 재수신한 메시지는 중복 여부를 확인해 금액에 다시 더하지 않아야 한다.

결국 이번 과제의 핵심은 집계 상태를 어디에 저장하고, 재시작할 때 어떻게 이어 쓸 것인지 정하는 데 있었다. 메모리에만 두었던 누적 금액을 SQLite에 저장하면서, Consumer가 종료돼도 집계 상태가 남도록 바꿀 수 있었다.


## 실습을 마치며

같은 그룹의 Consumer는 메시지를 각각 전부 받는 대신 파티션을 나눠 처리했다. `acks="all"` 추가 전후에는 기본 확인 조건이 같았으며, 측정된 지연 차이만으로 설정의 영향을 판단하기는 어려웠다. 마지막으로 집계 상태를 SQLite에 저장하면서, Consumer의 오프셋만 유지하는 것으로는 누적 집계를 복원할 수 없다는 점을 확인했다.

재시작 후에도 집계를 이어가려면 저장된 상태와 읽은 위치가 함께 관리돼야 한다. 여기에 중복 처리 방지를 더하면, 저장과 커밋 사이에 프로그램이 종료되더라도 같은 메시지를 누적 금액에 두 번 반영하는 문제를 막을 수 있다.

## AI 활용 안내

이 문서는 직접 실행한 실습 결과와 출력 로그를 바탕으로 작성했으며, 코드 수정 방법을 안내받고 결과를 해석하고 문장을 정리하는 과정에서 ChatGPT의 도움을 받았다. 측정값과 재시작 전후의 집계 금액은 실제 실행 결과를 사용했다.




