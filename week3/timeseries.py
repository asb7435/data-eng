import pandas as pd
 
df = pd.read_parquet('orders_step1.parquet')
customers = pd.read_csv('customers.csv', parse_dates=['joined'])
m = df.merge(customers, on='customer_id', how='left', validate='many_to_one')
 
# 일부러 실패 — 인덱스가 날짜가 아닌 채로 resample
try:
    m['amount'].resample('D').sum()
except TypeError as e:
    print('예상대로 실패:', e)

ts = m.set_index('order_date').sort_index()
print('인덱스 타입:', ts.index.dtype)
print('기간:', ts.index.min().date(), '~', ts.index.max().date())
print(ts.head(2))

daily = ts['amount'].resample('D').sum()
weekly_trend = daily.rolling(7).mean()
 
print('일별 매출 (마지막 3일)')
print(daily.tail(3))
print('7일 이동 평균 (마지막 3일)')
print(weekly_trend.round(0).tail(3))
 
print('daily 행 수:', len(daily))
print('rolling 행 수:', len(weekly_trend), '← 같습니다')

print(weekly_trend.head(8))

weekly = ts['amount'].resample('W').sum()
monthly = ts['amount'].resample('ME').agg(['sum', 'mean', 'count'])
 
print('주별 매출')
print(weekly)
print('\n월별 요약')
print(monthly.round(0))

print(m[['price', 'quantity', 'amount']].describe().round(0))
 
# 분위수로 분포 보기
print('\n주문 금액 분위수')
print(m['amount'].quantile([0.25, 0.5, 0.75, 0.9, 0.99]).round(0))
 
# 지역별 평균과 편차
print('\n지역별')
print(m.groupby('region')['amount'].agg(['mean', 'std', 'count']).round(0))

m.to_parquet('orders_enriched.parquet', index=False)
print('저장 완료:', len(m), '행,', len(m.columns), '열')
print('열 목록:', m.columns.tolist())



cust = m.groupby('customer_id').agg(
    orders=('order_id', 'count'),
    total=('amount', 'sum'),
    last_order=('order_date', 'max'),
).sort_values('total', ascending=False)
print(cust.head(10))
 
print(m.groupby('weekday')['amount'].mean().round(0).sort_values(ascending=False))
 
top = (m.groupby(['region', 'category'])['amount'].sum()
         .reset_index()
         .sort_values('amount', ascending=False)
         .groupby('region').head(1))
print(top)

