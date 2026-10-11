import requests
from bs4 import BeautifulSoup
 
res = requests.get('https://quotes.toscrape.com/', timeout=10)
soup = BeautifulSoup(res.text, 'html.parser')
 
 
def pick(el, selector, default=None):
    found = el.select_one(selector)
    return found.get_text(strip=True) if found else default
 
for q in soup.select('div.quote'):
    print(pick(q, 'small.author'), '|', pick(q, 'span.missing', '(없음)'))
