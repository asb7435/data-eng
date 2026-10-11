
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import pymysql
import requests
from bs4 import BeautifulSoup

BASE = "https://quotes.toscrape.com"
HEADERS = {"User-Agent": "data-eng-class-crawler/1.0 (learning purpose)"}
DELAY_SEC = 1.0
FAILED_LOG = Path("failed.log")

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "dataeng123",
    "database": "shop",
    "charset": "utf8mb4",
}


def log_failure(url: str, error: Exception | str) -> None:
    with FAILED_LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {url} | {error}\n")


def fetch(url: str, retries: int = 3) -> str:
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)

            if res.status_code == 429:
                last_error = RuntimeError("HTTP 429 Too Many Requests")
                print(f"429 응답 ({attempt}/{retries}), 5초 대기")
                time.sleep(5)
                continue

            res.raise_for_status()
            return res.text

        except requests.RequestException as e:
            last_error = e
            print(f"요청 실패 ({attempt}/{retries}): {e}")
            time.sleep(2 * attempt)

    log_failure(url, last_error)
    raise RuntimeError(f"{url} 수집 실패") from last_error


def parse(html: str) -> tuple[list[dict], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    for q in soup.select("div.quote"):
        rows.append({
            "author": q.select_one("small.author").get_text(strip=True),
            "quote_text": q.select_one("span.text").get_text(strip=True),
            "tags": ",".join(
                t.get_text(strip=True) for t in q.select("a.tag")
            ),
        })

    next_link = soup.select_one("li.next a")
    next_url = urljoin(BASE, next_link["href"]) if next_link else None

    return rows, next_url


def load(conn, rows: list[dict]) -> int:
    saved = 0

    with conn.cursor() as cur:
        for r in rows:
            saved += cur.execute(
                """
                INSERT IGNORE INTO quotes
                    (author, quote_text, tags, crawled_at)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    r["author"],
                    r["quote_text"],
                    r["tags"],
                    datetime.now(),
                ),
            )

    conn.commit()
    return saved


def run(max_pages: int = 10) -> None:
    url = BASE + "/"
    total_parsed = 0
    total_saved = 0

    conn = pymysql.connect(**DB_CONFIG)

    try:
        for page in range(1, max_pages + 1):
            try:
                html = fetch(url)
                rows, next_url = parse(html)
                saved = load(conn, rows)

            except Exception as e:
                conn.rollback()
                print(f"페이지 {page} 처리 실패: {e}")
                # fetch 실패는 fetch()에서 기록됨.
                # 그 외 파싱/DB 오류는 여기서 기록.
                if not isinstance(e, RuntimeError) or not str(e).endswith("수집 실패"):
                    log_failure(url, e)
                break

            total_parsed += len(rows)
            total_saved += saved

            print(f"page {page}: parsed {len(rows)}, saved {saved}")

            if not next_url:
                break

            url = next_url
            time.sleep(DELAY_SEC)

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM quotes")
            db_count = cur.fetchone()[0]

        print(f"\n이번 실행 파싱: {total_parsed}건")
        print(f"이번 실행 신규 저장: {total_saved}건")
        print(f"DB 전체 데이터: {db_count}건")

        if db_count == 100:
            print("검증 성공: DB에 100건이 있습니다.")
        else:
            print("검증 필요: DB 전체 건수가 100건이 아닙니다.")

    finally:
        conn.close()


if __name__ == "__main__":
    run()
