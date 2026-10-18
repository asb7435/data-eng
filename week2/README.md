# 2주차 산출물 — 쇼핑몰 ERD 설계 + 크롤링 파이프라인

## 1. ERD 설계서
- [ERD_설계서.md](ERD_설계서.md): 엔터티 정의 · 관계 · 정규화 근거 · 주문 가격 보존 결정
- [shopping_mall_erd.sql](shopping_mall_erd.sql): 설계서와 일치하는 MySQL 8 테이블 및 FK 정의
- 표 4개: customers · products · orders · order_items
- N:M(주문↔상품)을 order_items 교차 표로 해소

## 2. 크롤러
- 대상: https://quotes.toscrape.com (check_robots.py로 수집 허용 확인)
- 구조: fetch(수집) → parse(정제) → load(적재) 3함수 분리
- 예절: User-Agent 표기 · 요청 간격 1초 · robots.txt 사전 확인
- 기본 실행: 최대 10페이지 수집 (`run(max_pages=10)`)
- 중복 방지: quotes 표의 UNIQUE(author, quote_text) 제약 + INSERT IGNORE
- DB_CONFIG 상수로 접속 설정 관리, run()에서 연결 한 번 생성 후 load(conn, rows)에 전달
- 페이지 처리 실패 시 rollback 및 failed.log 기록, 마지막 SELECT COUNT(*)로 100건 확인

## 3. 실행 방법
WSL2 Ubuntu 등 bash 환경에서 week2 폴더를 기준으로 실행한다. Docker 컨테이너 `de-mysql`과 `shop` 데이터베이스가 준비되어 있어야 한다.

```bash
docker start de-mysql
docker exec de-mysql mysqladmin ping --silent  # mysqld is alive 확인 후 진행
python3 -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4 pymysql
```

`crawler_pipeline.py`의 DB_CONFIG를 로컬 DB 설정과 맞춘다. 최초 실행 전 [quotes.sql](quotes.sql)을 `shop`에 적용한다. 기존 데이터는 삭제하지 않는다.

```bash
python3 - <<'PY'
from pathlib import Path
import pymysql
from crawler_pipeline import DB_CONFIG

conn = pymysql.connect(**DB_CONFIG)
try:
    with conn.cursor() as cur:
        cur.execute(Path('quotes.sql').read_text(encoding='utf-8'))
    conn.commit()
finally:
    conn.close()
PY
python3 check_robots.py
python3 crawler_pipeline.py  # 최대 10페이지 수집·적재
```

쇼핑몰 DDL은 크롤러용 quotes 표와 별개다. MySQL 클라이언트에서 `shop` 데이터베이스를 선택하고 `shopping_mall_erd.sql`을 실행한다.

## 4. 실제 실행 검증 결과
피드백 반영 시 로컬 MySQL에서 재실행하여 확인했다.

| 실행 | 페이지별 결과 | 총 파싱 | 신규 저장 | DB 전체 건수 |
|---|---|---:|---:|---:|
| quotes 표 생성 후 첫 실행 | 1~10페이지 각각 parsed 10 / saved 10 | 100 | 100 | 100 |
| 동일 코드 재실행 | 1~10페이지 각각 parsed 10 / saved 0 | 100 | 0 | 100 |

- 두 실행 모두 마지막에 `검증 성공: DB에 100건이 있습니다.` 출력 확인
- 재실행 시 UNIQUE 제약으로 중복 저장이 방지됨
- shopping_mall_erd.sql은 별도 임시 데이터베이스에 적용해 FK 오류 1452·1451을 확인한 뒤 임시 DB 삭제

## 5. 남은 개선점
- tags를 쉼표 문자열로 저장 중이므로 quote_tags 교차 표로 분리해 태그별 검색과 집계를 개선할 예정
- DB 연결 생성이 try 밖에 있어 접속 실패는 failed.log에 기록되지 않으므로 연결 단계도 예외 처리 범위에 포함할 예정
- 페이지 처리 실패 후에도 최종 건수가 100이면 성공 문구가 나올 수 있으므로 이번 실행의 완료 여부와 DB 전체 건수 검증을 분리할 예정

## 6. MySQL 실행 문제와 해결 기록
주말에 실습을 다시 진행할 때 MySQL이 실행되지 않아 시간을 썼다. 당시 원인을 기록하지 않아 확정할 수는 없다. 이번 재점검에서는 `docker ps -a`로 de-mysql이 `Exited (255)` 상태임을 확인했고, `docker start de-mysql`로 시작했다. 시작 직후에는 연결 오류가 발생했으며 서버 준비 후 다시 연결했다. 이후 `shop.quotes`가 없어 오류 1146이 발생하여 quotes.sql로 표를 생성한 뒤 100건 수집과 중복 방지를 확인했다. 다음 실습에서는 컨테이너 상태 → 서버 준비 여부 → 대상 DB·테이블 존재 여부 순서로 확인한다.
