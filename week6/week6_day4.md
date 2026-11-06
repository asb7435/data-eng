# WEEK6 DAY4 MINI

## 1. 컬럼 추가 후 이벤트 스키마 변화 확인

`shop.orders` 테이블에 주문 메모를 저장할 `memo` 컬럼을 추가했다.

```bash
docker exec -i mysql mysql -uroot -prootpw shop <<SQL
ALTER TABLE orders ADD COLUMN memo VARCHAR(100);
DESC orders;
SQL
```

실습 중 같은 명령을 다시 실행했을 때는 다음 오류가 나왔다.

```text
ERROR 1060 (42S21): Duplicate column name 'memo'
```

이미 `memo` 컬럼이 추가된 상태에서 다시 추가하려고 했기 때문이다. 이후 스키마 이력 토픽에서 해당 ALTER 문과 추가된 컬럼 정보를 확인했다.

### INSERT 후 확인할 내용

컬럼 추가 이력은 확인했지만, 이번에 정리한 로그에는 컬럼 추가 후 INSERT한 데이터 변경 이벤트가 포함돼 있지 않다. 따라서 이벤트 스키마까지 바뀌었다는 결과는 아직 확정하지 않았다.

이 부분은 다음 순서로 추가 확인할 수 있다.

먼저 터미널 하나에서 데이터 변경 토픽을 구독한다. 구독이 시작된 뒤 다른 터미널에서 INSERT를 실행한다.

```bash
# 터미널 1: 새 데이터 변경 이벤트 확인
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic shop.shop.orders
```

```bash
# 터미널 2: 메모를 포함한 주문 추가
docker exec -i mysql mysql -uroot -prootpw shop <<SQL
INSERT INTO orders (customer, amount, memo)
VALUES ('user6', 15000, '배송 전 연락 부탁드립니다');
SQL
```

새 INSERT 이벤트에서 확인할 항목은 다음과 같다. 아래는 확인 기준이며, 실제 출력 결과를 옮긴 내용은 아니다.

- `payload.op`가 INSERT를 뜻하는 `c`인지 확인한다.
- `payload.after.memo`에 입력한 메모가 들어 있는지 확인한다.
- `schema`의 `after` 구조에 `memo` 필드가 추가됐는지 확인한다.
- 기존 컬럼에 더해 `memo`가 문자열이며 NULL을 허용하는 필드로 표현되는지 확인한다.

## 2. schema-changes.shop에 기록된 내용 확인

다음 명령으로 내부 스키마 이력 토픽을 처음부터 읽었다.

```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic schema-changes.shop \
  --from-beginning \
  --property print.key=true
```

첫 번째 조회에서는 총 7개의 메시지가 출력됐다. 초기 스키마 정보와 함께 `memo` 컬럼을 추가한 변경 이력이 남아 있었다.

### 컬럼 추가 이력

출력에는 실제로 실행된 ALTER 문이 기록돼 있었다.

```json
{
  "databaseName": "shop",
  "ddl": "ALTER TABLE orders ADD COLUMN memo VARCHAR(100)"
}
```

`tableChanges`의 변경 종류는 `ALTER`였고, 변경 후 테이블의 컬럼 목록에 다음 정보가 추가돼 있었다. 아래는 전체 출력에서 필요한 필드만 발췌한 것이다.

```json
{
  "name": "memo",
  "typeName": "VARCHAR",
  "length": 100,
  "position": 5,
  "optional": true
}
```

| 항목 | 확인한 값 | 의미 |
|---|---|---|
| `name` | `memo` | 추가된 컬럼 이름 |
| `typeName` | `VARCHAR` | 문자열 자료형 |
| `length` | `100` | 최대 길이 |
| `position` | `5` | 다섯 번째 컬럼 |
| `optional` | `true` | NULL 허용 |

변경이 발생한 binlog 위치도 함께 기록돼 있었다.

```json
"position": {
  "ts_sec": 1793715142,
  "file": "binlog.000002",
  "pos": 4697,
  "server_id": 1
}
```

이 토픽에는 구조 변경 SQL뿐 아니라 변경 후 테이블 구조와 해당 변경이 발생한 위치도 저장된다는 것을 확인했다.

### 초기 스키마 기록에서 확인한 점

앞부분에는 `snapshot: true`인 초기 스키마 기록이 있었다. 여기에 문자 인코딩 설정, 데이터베이스와 테이블의 DROP·CREATE 문, 기존 컬럼 구조가 포함돼 있었다. 이 기록에 DROP 문이 있다는 사실만으로 실습 중 실제 데이터베이스가 삭제됐다고 판단할 수는 없다. 초기 스키마 복원을 위한 이력이라는 맥락에서 봐야 한다.

또한 `print.key=true`로 조회했을 때 JSON 앞에 나온 `null`은 메시지 키가 없다는 뜻이다. 메시지 값에는 JSON이 있으므로, 값이 없는 툼스톤과는 다르다.

### 정리

`shop.shop.orders`는 주문 데이터의 변경을 담고, 이번 설정의 `schema-changes.shop`은 Debezium이 사용하는 내부 스키마 이력을 담는다. 데이터가 어떻게 바뀌었는지와 테이블 구조가 어떻게 바뀌었는지를 서로 다른 토픽에서 확인할 수 있었다.

## 3. 커넥터 삭제 후 재등록하면 스냅숏을 다시 할까?

커넥터를 삭제한 뒤 같은 이름과 설정으로 다시 등록했다. 새 메시지 발생 여부를 비교하기 위해 실험 중에는 MySQL 데이터를 변경하지 않았다.

### 삭제 전 끝 오프셋 확인

```bash
docker exec kafka /opt/kafka/bin/kafka-get-offsets.sh \
  --bootstrap-server localhost:9092 \
  --topic shop.shop.orders
```

```text
shop.shop.orders:0:19
```

### 커넥터 삭제

```bash
curl -i -X DELETE http://localhost:8083/connectors/mysql-cdc
```

응답은 `204 No Content`로, 삭제가 정상적으로 처리됐다.

### 같은 설정으로 재등록

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  --data @register-mysql.json \
  http://localhost:8083/connectors
```

이어서 상태를 확인했다.

```bash
curl -s http://localhost:8083/connectors/mysql-cdc/status \
  | python3 -m json.tool
```

커넥터와 0번 태스크의 상태가 모두 `RUNNING`으로 나왔다.

### 재등록 후 끝 오프셋 확인

같은 `kafka-get-offsets.sh` 명령을 다시 실행한 결과는 다음과 같았다.

```text
shop.shop.orders:0:19
```

| 확인 항목 | 결과 |
|---|---|
| 삭제 전 끝 오프셋 | 19 |
| DELETE 응답 | 204 No Content |
| 재등록 후 커넥터 상태 | RUNNING |
| 재등록 후 태스크 상태 | RUNNING |
| 재등록 후 끝 오프셋 | 19 |

끝 오프셋이 19에서 변하지 않았으므로, 확인 시점까지 새로운 스냅숏 레코드가 추가되지 않았다. 커넥터를 다시 등록해도 기존 데이터를 처음부터 다시 발행하지 않은 것이다.

여기서 끝 오프셋 19는 다음 메시지가 기록될 위치이며, 현재 MySQL 테이블에 19행이 있다는 뜻은 아니다.

### 어디에 이전 처리 상태가 남아 있을까?

수업의 Kafka Connect 설정에는 다음 항목이 있다.

```yaml
OFFSET_STORAGE_TOPIC: connect_offsets
```

Kafka Connect는 이 토픽에 소스 커넥터의 처리 위치를 저장한다. Debezium의 스냅숏 상태도 소스 오프셋의 일부로 관리된다. 커넥터를 삭제해도 저장된 오프셋이 함께 없어지는 것은 아니므로, 같은 이름과 소스 설정으로 다시 등록하면 남아 있는 기록을 이용해 이전 위치에서 이어서 처리할 수 있다.

이번 실습에서는 `connect_offsets`의 내용을 직접 해석하지는 않았다. 재등록 전후 끝 오프셋이 유지된 결과와 Connect의 저장 설정을 바탕으로 동작을 이해했다.

| 토픽 | 역할 |
|---|---|
| `connect_offsets` | 처리 위치와 스냅숏 상태 저장 |
| `schema-changes.shop` | 테이블 구조를 복원하기 위한 스키마 이력 저장 |
| `shop.shop.orders` | 주문 데이터의 변경 이벤트 저장 |

따라서 커넥터를 삭제하는 것과 이전 처리 상태를 초기화하는 것은 별개의 작업이다. 이번처럼 기존 오프셋과 이력이 유지된 조건에서는 재등록 후에도 이전 상태를 이어갈 수 있었다.

## 실습을 마치며

스키마 이력 토픽에서 `memo` 컬럼의 추가 SQL과 변경 후 컬럼 정보를 확인했다. 또 커넥터를 삭제하고 다시 등록해도 데이터 토픽의 끝 오프셋이 19로 유지되는 것을 확인했다. 커넥터 설정을 삭제하더라도 처리 위치와 스키마 이력은 Kafka에 별도로 남는다는 점을 이해할 수 있었다.

컬럼 추가 후 INSERT 이벤트에 `memo`가 반영되는지는 실제 출력으로 추가 확인해야 한다. 내부 스키마 이력에 컬럼이 기록된 것과 데이터 변경 이벤트의 스키마를 직접 확인한 것은 구분해서 정리했다.

## AI 활용 안내

이 문서는 직접 실행한 실습의 출력 로그와 수업 자료를 바탕으로 정리했다. 명령어 안내, 출력 해석, 문장 작성 과정에서 ChatGPT의 도움을 받았다. 확인한 결과와 추가 확인이 필요한 내용은 구분해 표시했다.

