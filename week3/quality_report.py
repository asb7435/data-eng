# quality_report.py — 주문 품질 지표 측정
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent


def profile(df: pd.DataFrame, name: str) -> pd.DataFrame:
    return pd.DataFrame({
        'dataset': [name],
        'rows': [len(df)],
        'dup_order_id': [int(df['order_id'].duplicated().sum())],
        'null_price': [int(df['price'].isna().sum())],
        'null_rate_pct': [round(df['price'].isna().mean() * 100, 2)],
        'category_values': [df['category'].nunique()],
        # 결측은 범위 위반과 별도로 집계한다.
        'price_le_0': [int((df['price'] <= 0).sum())],
        'quantity_le_0': [int((df['quantity'] <= 0).sum())],
        'quantity_ge_6': [int((df['quantity'] >= 6).sum())],
    })


def main():
    raw = pd.read_csv(BASE / 'orders.csv')
    cleaned = pd.read_parquet(BASE / 'orders_clean.parquet')
    report = pd.concat([profile(raw, 'before'), profile(cleaned, 'after')], ignore_index=True)
    report.to_csv(BASE / 'quality_report.csv', index=False, encoding='utf-8')
    print(report.to_string(index=False))


if __name__ == '__main__':
    main()
