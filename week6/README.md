# 6주차 산출물 — 실시간 CDC 파이프라인

## 1\. 구성

|서비스|역할|포트|
|-|-|-|
|kafka|이벤트 중간 저장소|9092(외부) · 29092(내부)|
|mysql|원천 DB|3306|
|connect|Debezium 소스 + S3 싱크|8083|
|minio|적재 대상 (S3 호환)|9000 · 9001|

## 2\. 데이터 흐름

MySQL(binlog) → Debezium → Kafka(shop.shop.orders) → S3 Sink → MinIO(cdc-raw)

## 3\. 토픽 구성

|토픽|용도|
|-|-|
|orders|6-3 파이썬 실습용|
|shop.shop.orders|CDC 변경 이벤트|
|schema-changes.shop|스키마 변경 이력|
|connect\_configs/offsets/statuses|Connect 내부 상태|

## 4\. 제출 파일

* docker-compose.yml
* register-mysql.json (Debezium 소스 커넥터)
* sink-minio.json (S3 싱크 커넥터)

## 5\. 확인한 것

* op = r/c/u/d 네 종류를 모두 관찰
* MySQL INSERT → MinIO 파일 생성까지 엔드투엔드 통과
* flush.size 만큼 모여야 파일이 생기는 것을 확인

## 6\. 남은 개선점

아직 없음...
프로세스를 이해할동 말동 하면서 혼자 풀다 막히면 GPT한테 헬프 치다가 순서는 잘 따라하는데 내용이 내가 생각하는게 맞나 싶으면 아 이게 맞는지 GPT한테 한번 확인해달라하고 정 이해 안가면 이 프로세스를 이미지화 해달라고 하면서 이미지로 이해 하는데 아직 연습을 몇번 더 해봐야 그림이 자연스럽게 그려거 같지만

짬짬히 지난 수업을 복습하는데 아직 6주차에 도달하기엔 시간이 걸릴거 같고 일단 이해를 우선으로 하며 진도가 놓쳐 하다 말거 같아 진도를 우선시 하되 복습을 짬짬히 이어 나가고 있습니다.
이번 6주차 남은 4,5일차는 실습이 힘들거 같아 미리 달리고 있습니다.


