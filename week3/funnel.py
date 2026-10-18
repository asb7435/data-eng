# funnel.py — 퍼널 단계별 사용자 수와 전환율 구하기
import duckdb

print(duckdb.sql("""
    -- 사용자별로 각 이벤트를 한 번이라도 했는지 확인
    WITH per_user AS (
        SELECT user_id,
               -- 조회한 적이 있으면 1, 없으면 0
               max(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS viewed,
               -- 장바구니에 담은 적이 있으면 1, 없으면 0
               max(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END) AS carted,
               -- 구매한 적이 있으면 1, 없으면 0
               max(CASE WHEN event_type = 'buy' THEN 1 ELSE 0 END) AS bought
        FROM 'events.parquet'
        -- 사용자별로 묶어서 같은 이벤트를 여러 번 해도 한 명으로 계산
        GROUP BY user_id
    )
    SELECT sum(viewed) AS viewed,  -- 조회 사용자 수
           sum(carted) AS carted,  -- 장바구니 사용자 수
           sum(bought) AS bought,  -- 구매 사용자 수

           -- 조회 → 장바구니 전환율 (%), 소수점 첫째 자리까지 표시
           round(sum(carted) * 100.0 / nullif(sum(viewed), 0), 1) AS view_to_cart,

           -- 장바구니 → 구매 전환율 (%)
           -- nullif는 분모가 0이면 NULL로 바꿔 0으로 나누는 것을 방지
           round(sum(bought) * 100.0 / nullif(sum(carted), 0), 1) AS cart_to_buy
    FROM per_user
"""))

# 이벤트가 발생한 시간 순서는 확인하지 않고, 발생 여부만으로 집계
