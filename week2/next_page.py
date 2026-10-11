import requests
from bs4 import BeautifulSoup
 
res = requests.get('https://quotes.toscrape.com/', timeout=10)
soup = BeautifulSoup(res.text, 'html.parser')
 
next_link = soup.select_one('li.next a')
print('next href:', next_link['href'] if next_link else None)
 
# 마지막 페이지에서는 None이 나옵니다 — 순회를 멈추는 신호가 됩니다
res_last = requests.get('https://quotes.toscrape.com/page/10/', timeout=10)
soup_last = BeautifulSoup(res_last.text, 'html.parser')
print('last page next:', soup_last.select_one('li.next a'))

