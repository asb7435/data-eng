import pandas as pd
from clean_orders import load_raw, clean
 
first = clean(load_raw())
second = clean(load_raw())
 
print('행 수 같은가 :', len(first) == len(second))
print('내용 같은가 :', first.equals(second))
 
# 저장했다 읽어도 같은지
first.to_parquet('t1.parquet', index=False)
second.to_parquet('t2.parquet', index=False)
print('파일로도 같은가:', pd.read_parquet('t1.parquet').equals(pd.read_parquet('t2.parquet')))

