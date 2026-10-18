# quality_mini.py — 결측 처리 비교와 100만 행 품질 측정 시간 비교
from pathlib import Path
from time import perf_counter
import duckdb
import pandas as pd
from quality_report import profile

BASE = Path(__file__).resolve().parent
REPEATS = 5

# 모든 품질 지표를 DuckDB SQL 한 번으로 계산한다.
EVENT_SQL = """
SELECT count(*) AS rows,
       count(event_id) - count(DISTINCT event_id) AS dup_event_id,
       count(*) - count(event_id) AS null_event_id,
       count(*) - count(user_id) AS null_user_id,
       count(*) - count(event_type) AS null_event_type,
       count(*) - count(value) AS null_value,
       count(*) - count(ts) AS null_ts,
       count(DISTINCT event_type) AS event_type_values,
       count(*) FILTER (WHERE user_id <= 0) AS user_id_le_0,
       count(*) FILTER (WHERE value <= 0) AS value_le_0,
       count(*) FILTER (WHERE event_type NOT IN ('view', 'cart', 'buy')) AS unknown_event_type,
       min(ts) AS first_ts, max(ts) AS last_ts
FROM read_parquet(?)
"""


def pandas_events(df):
    # SQL과 동일하게 ID 결측은 중복 수에서 제외하고 별도로 센다.
    return {
        'rows': len(df),
        'dup_event_id': int(df.event_id.dropna().duplicated().sum()),
        'null_event_id': int(df.event_id.isna().sum()),
        'null_user_id': int(df.user_id.isna().sum()),
        'null_event_type': int(df.event_type.isna().sum()),
        'null_value': int(df.value.isna().sum()),
        'null_ts': int(df.ts.isna().sum()),
        'event_type_values': df.event_type.nunique(),
        'user_id_le_0': int((df.user_id <= 0).sum()),
        'value_le_0': int((df.value <= 0).sum()),
        'unknown_event_type': int((df.event_type.notna() & ~df.event_type.isin(['view', 'cart', 'buy'])).sum()),
        'first_ts': df.ts.min(), 'last_ts': df.ts.max(),
    }


def measure(fn):
    start = perf_counter()
    result = fn()
    return result, perf_counter() - start


def main():
    raw = pd.read_csv(BASE / 'orders.csv')
    # 2方式で共通の処理を先に行い、価格欠損の扱いだけを変える。
    common = raw.copy()
    common['category'] = common.category.str.strip()
    common['order_date'] = pd.to_datetime(common.order_date)
    common = common.drop_duplicates('order_id', keep='first')
    filled = common.copy()
    filled['price'] = filled.price.fillna(filled.price.median())
    dropped = common.dropna(subset=['price']).copy()
    methods = [('median', filled), ('drop', dropped)]
    reports = [profile(raw, 'before')]
    stats = []
    for name, df in methods:
        df['amount'] = df.price * df.quantity
        df.to_parquet(BASE / f'orders_clean_{name}.parquet', index=False)
        reports.append(profile(df, name))
        stats.append({'method': name, 'rows': len(df),
                      'removed_vs_raw': len(raw)-len(df),
                      'price_mean': df.price.mean(), 'price_median': df.price.median(),
                      'price_std': df.price.std(), 'quantity_mean': df.quantity.mean(),
                      'amount_mean': df.amount.mean(), 'amount_total': df.amount.sum()})
    pd.concat(reports, ignore_index=True).to_csv(BASE / 'quality_report_compare.csv', index=False)
    comparison = pd.DataFrame(stats)
    comparison.to_csv(BASE / 'orders_method_comparison.csv', index=False)
    print('\n주문 결측 처리 비교\n', comparison.to_string(index=False))

    # 범위 검사기가 실제 위반을 탐지하는지 작은 복사본으로 확인한다.
    bad = filled.head(3).copy()
    bad.iloc[0, bad.columns.get_loc('price')] = 0
    bad.iloc[1, bad.columns.get_loc('quantity')] = 6
    checks = profile(bad, 'bad').iloc[0]
    assert checks.price_le_0 == 1 and checks.quantity_ge_6 == 1

    path = str(BASE / 'events.parquet')
    con = duckdb.connect()
    # Pandas 변환 시간은 DuckDB 측정에서 제외하기 위해 fetchone()을 사용한다.
    def sql_events():
        cursor = con.execute(EVENT_SQL, [path])
        names = [column[0] for column in cursor.description]
        return dict(zip(names, cursor.fetchone()))

    def pd_events():
        return pandas_events(pd.read_parquet(path))

    # 두 방식 모두 1회 워밍업 후, 실행 순서를 번갈아 5회 측정한다.
    sql_events()
    pd_events()
    times = []
    for run in range(1, REPEATS + 1):
        order = [('duckdb_sql', sql_events), ('pandas', pd_events)]
        if run % 2 == 0:
            order.reverse()
        results = {}
        for name, fn in order:
            result, seconds = measure(fn)
            results[name] = result
            times.append({'run': run, 'method': name, 'seconds': seconds})
        assert results['duckdb_sql'] == results['pandas'], '품질 지표 불일치'
    pd.DataFrame([{'dataset': 'events', **results['duckdb_sql']}]).to_csv(BASE / 'events_quality_report.csv', index=False)
    timing = pd.DataFrame(times)
    timing.to_csv(BASE / 'events_quality_timing.csv', index=False)
    summary = timing.groupby('method', as_index=False).seconds.agg(['median', 'min', 'max']).reset_index()
    summary.to_csv(BASE / 'events_quality_timing_summary.csv', index=False)
    print('\n이벤트 품질\n', results['duckdb_sql'])
    print('\n읽기 + 품질 집계 + 결과 반환 시간(초)\n', summary.to_string(index=False))
    con.close()
    print('두 방식의 모든 이벤트 품질 지표 일치 / 범위 검사기 검증 통과')


if __name__ == '__main__':
    main()

