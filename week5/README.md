# 5주차 산출물 — 일별 매출 데이터 마트

## 1. 구성
- 클러스터: Spark Standalone 3.5.3 · Docker Compose
- 마스터 1개 + 워커 2개 (워커당 CPU 2코어, 메모리 2GiB)
- 저장소: MinIO (s3a) · Iceberg 1.5.2 (hadoop 카탈로그)
- 배치: mart.py · 저장 테이블: lake.db.daily_sales_mart

## 2. 처리 흐름
1. 샘플 주문 5행과 상품 3행으로 DataFrame 생성
2. 날짜 인자가 있으면 해당 날짜만 필터링
3. product_id로 조인 후 amount = qty × price 계산
4. 날짜별 daily_amount와 order_cnt 집계
5. coalesce(1) 후 Iceberg 테이블을 createOrReplace로 교체 저장
6. 저장 결과를 날짜순으로 조회

## 3. 실행
```bash
cd /home/sban/data-eng/week5
docker compose cp mart.py spark-master:/tmp/mart.py
docker compose exec -T spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.jars.ivy=/tmp/.ivy2 \
  --packages org.apache.hadoop:hadoop-aws:3.3.4,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2 \
  /tmp/mart.py > mart.log 2>&1
status=$?
echo "종료 코드: $status"
```
날짜를 지정하려면 /tmp/mart.py 뒤에 2026-08-24처럼 인자를 추가한다. 특정 날짜 실행도 테이블 전체를 교체하므로 전체 결과 제출 시 날짜 인자를 생략한다.

## 4. 실측 및 측정 상태
| 항목 | 값 / 상태 |
|---|---|
| 워커 수 / 전체 CPU 코어 수 | 2개 / 4코어 |
| 입력 주문 / 상품 | 5행 / 3행 |
| 출력 마트 | 3행 |
| 기본 파티션 수 | 미측정 (입력과 셔플 파티션을 구분하여 추가 기록 필요) |
| AQE 끔 · shuffle.partitions 200 → 8 실행 시간 | 미측정 |
| coalesce(1) 전/후 데이터 파일 수 | 미측정 (코드 적용은 확인) |
| 스큐 Task 시간 Max / Median | 미측정 |

기존 mart.log에 성능 실측값이 없어 임의 수치를 넣지 않았다. 위 성능 항목은 추가 측정 후 갱신해야 한다.

## 5. 마트 조회 결과
기존 mart.log에서 확인한 실제 결과다.
```text
[mart] 대상 날짜: 전체
[mart] 원천 5행
[mart] 마트 3행
+----------+------------+---------+
|order_date|daily_amount|order_cnt|
+----------+------------+---------+
|2026-08-24|      113000|        2|
|2026-08-25|     1155000|        2|
|2026-08-26|       46000|        1|
+----------+------------+---------+
[mart] 완료
```
전체 매출은 1,314,000이며 주문은 총 5건이다.

## 6. 확인한 것
- 실행 확인: 입력 5행, 출력 3행, 결과 표와 완료 메시지를 로그에서 확인했다.
- 코드 확인: createOrReplace로 같은 입력의 행이 누적되지 않는 구조다. 두 번 실행한 결과 동일성 비교는 추가 검증이 필요하다.
- 코드 확인: 없는 날짜는 sys.exit(1)로 종료한다. 실제 종료 코드 검증은 추가로 필요하다.
- coalesce(1) 적용은 확인했다. 실제 파일 수는 현재 Iceberg 데이터 파일과 이전 스냅샷 파일, 메타데이터를 구분하여 측정해야 한다.
- 트러블슈팅: 이전 PySpark 세션이 4코어를 점유했다. 이전 세션 종료 후 현재 세션이 자원을 받아 orders.show()가 성공했다.

## 7. 제출 파일
- mart.py: 배치 스크립트
- mart.log: 실행 로그 및 조회 결과
- README.md: 구성, 실행 방법, 결과 정리

성능 실측값은 추가 측정 전이므로 수치 제출까지 완료된 상태는 아니다.
