import requests
from bs4 import BeautifulSoup

API_KEY = "092628db181070b29e5db5561632483c"
PRODUCT_URL = "https://www.flipkart.com/apple-iphone-13/p/itm6c601bfef8f5b"

url = f"http://api.scraperapi.com?api_key={API_KEY}&url={PRODUCT_URL}"

print("🔍 Fetching via ScraperAPI...")
r = requests.get(url)
print("Status:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

# Hunt for price
for tag in soup.find_all(True):
    if '₹' in tag.text and len(tag.text.strip()) < 15:
        print(f"Tag: {tag.name}, Class: {tag.get('class')}, Text: {tag.text.strip()}")