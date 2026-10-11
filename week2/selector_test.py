import requests
from bs4 import BeautifulSoup
 
res = requests.get('https://quotes.toscrape.com/', timeout=10)
soup = BeautifulSoup(res.text, 'html.parser')
 
print(soup.select('div.quotes'))          
print(soup.select_one('span.txt'))        
print(soup.select_one('span.txt').get_text())  