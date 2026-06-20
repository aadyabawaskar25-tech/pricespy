import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

API_KEY = "092628db181070b29e5db5561632483c"

products = [
    {"name": "iPhone 13 128GB", "url": "https://www.amazon.in/Apple-iPhone-13-128GB-Midnight/dp/B09G9HD6PD"},
    {"name": "Samsung Galaxy S23", "url": "https://www.amazon.in/Samsung-Galaxy-S23-Phantom-Storage/dp/B0BT9CXXXX"},
    {"name": "REDTIGER F17 Dash Cam", "url": "https://www.amazon.in/REDTIGER-F17-Elite-Channel-STARVIS/dp/B0F8NNYZPV"},
    {"name": "Lifelong ZenCharge Power Bank", "url": "https://www.amazon.in/Lifelong-ZenCharge-Compact-Lithium-Charging/dp/B0D5HTDWSC"},
    {"name": "boAt EnergyShroom 10000mAh", "url": "https://www.amazon.in/boAt-EnergyShroom-10000mAh-Magnetic-Powerbank/dp/B0F4XRZ81C"},
    {"name": "boAt Airdopes Earphones", "url": "https://www.amazon.in/boAt-Airdopes-Multidevice-Bluetooth-Earphones/dp/B0F8BVYRWS"},
    {"name": "Noise Wireless Earbuds", "url": "https://www.amazon.in/Noise-Launched-Wireless-AirWaveTM-Technology/dp/B0DGV56J6G"},
    {"name": "Apple iPad Air 11 inch", "url": "https://www.amazon.in/Apple-iPad-Air-27-59-11/dp/B0GQVHBK9M"},
]

def scrape_price(product):
    api_url = "http://api.scraperapi.com?api_key=" + API_KEY + "&url=" + product["url"] + "&country_code=in"
    try:
        r = requests.get(api_url, timeout=60)
        soup = BeautifulSoup(r.text, "html.parser")
        
        price = soup.find("span", {"class": "a-price-whole"})
        if not price:
            price = soup.find("span", {"class": "a-offscreen"})
        
        return price.text.strip() if price else "Not found"
    except Exception as e:
        return f"Error: {e}"

# Load existing history
try:
    with open("price_history.json", "r") as f:
        history = json.load(f)
except:
    history = []

today = datetime.now().strftime("%Y-%m-%d")
print(f"🚀 Starting scrape for {today}\n")

for product in products:
    print(f"Fetching: {product['name']}...")
    price = scrape_price(product)
    print(f"Price: {price}")
    
    history.append({
        "name": product["name"],
        "price": price,
        "date": today,
        "url": product["url"]
    })
    
    time.sleep(2)

with open("price_history.json", "w") as f:
    json.dump(history, f, indent=2)

print(f"\n✅ Done! {len(products)} products scraped and saved!")