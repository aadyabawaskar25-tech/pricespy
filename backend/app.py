from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)  # allows your GitHub Pages frontend to call this backend

API_KEY = "092628db181070b29e5db5561632483c"


def clean_price(text):
    """Turn '₹1,899.00' into 1899.0"""
    if not text:
        return None
    digits = re.sub(r"[^0-9.]", "", text)
    try:
        return float(digits)
    except:
        return None


def search_amazon(query):
    """Search Amazon.in for a product and return top results with price + MRP."""
    search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    api_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={search_url}&country_code=in"

    r = requests.get(api_url, timeout=60)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    # Amazon search result cards
    cards = soup.select('div[data-component-type="s-search-result"]')

    for card in cards[:8]:  # limit to top 8 results
        name_tag = card.select_one("h2 span")
        name = name_tag.text.strip() if name_tag else None

        price_tag = card.select_one("span.a-price > span.a-offscreen")
        price = clean_price(price_tag.text) if price_tag else None

        mrp_tag = card.select_one("span.a-price.a-text-price > span.a-offscreen")
        mrp = clean_price(mrp_tag.text) if mrp_tag else None

        link_tag = card.select_one("h2 a")
        link = "https://www.amazon.in" + link_tag["href"] if link_tag and link_tag.get("href") else None

        img_tag = card.select_one("img.s-image")
        image = img_tag["src"] if img_tag else None

        if name and price:
            results.append({
                "name": name,
                "price": price,
                "mrp": mrp,
                "url": link,
                "image": image,
            })

    return results


def get_verdict(price, mrp):
    """Decide if a discount looks real or suspicious based on price vs MRP gap."""
    if not mrp or not price or mrp <= 0:
        return {"label": "No Discount Data", "cls": "tracking"}

    discount_pct = ((mrp - price) / mrp) * 100

    if discount_pct <= 0:
        return {"label": "No Discount", "cls": "tracking"}
    elif discount_pct < 15:
        return {"label": "Modest Discount", "cls": "tracking"}
    elif discount_pct < 40:
        return {"label": "Likely Real", "cls": "real"}
    else:
        # very large claimed discounts are the most commonly inflated
        return {"label": "Verify Before Buying", "cls": "fake"}


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Missing search query"}), 400

    try:
        results = search_amazon(query)
        for item in results:
            verdict = get_verdict(item["price"], item["mrp"])
            item["verdict"] = verdict["label"]
            item["verdict_class"] = verdict["cls"]
            if item["mrp"]:
                item["discount_pct"] = round(((item["mrp"] - item["price"]) / item["mrp"]) * 100, 1)
            else:
                item["discount_pct"] = None

        return jsonify({"query": query, "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"status": "PriceSpy backend is running"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
