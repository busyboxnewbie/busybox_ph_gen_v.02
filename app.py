from flask import Flask, render_template, request, redirect, url_for, jsonify
from bs4 import BeautifulSoup
import requests
import re
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PRODUCTS_FILE = "products.json"

try:
    with open(PRODUCTS_FILE, "r") as f:
        products = json.load(f)
except FileNotFoundError:
    products = {
        "shopee": [],
        "lazada": [],
        "amazon": [],
        "digital": []
    }

categories = {
    "Home & Living": {
        "Bath": ["Bath Towel Rack"],
        "Kitchen": ["Cookware"]
    },
    "Electronics": {
        "Phones": ["Smartphones"],
        "Computers": ["Laptops"]
    }
}

def get_product_details(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        title = ""
        price = ""
        image_url = ""

        if "shopee.ph" in url:
            title_element = soup.find("div", class_=re.compile(r"product-detail__header"))
            if title_element:
                title = title_element.text.strip()
            price_element = soup.find("div", class_=re.compile(r"product-detail__price"))
            if price_element:
                price = price_element.text.strip()
            image_element = soup.find("img", class_=re.compile(r"product-detail__image"))
            if image_element:
                image_url = image_element["src"]

        elif "lazada.com.ph" in url:
            title_element = soup.find("h1", class_=re.compile(r"product-title"))
            if title_element:
                title = title_element.text.strip()
            price_element = soup.find("span", class_=re.compile(r"product-price"))
            if price_element:
                price = price_element.text.strip()
            image_element = soup.find("img", class_=re.compile(r"product-image"))
            if image_element:
                image_url = image_element["src"]

        elif "amazon.com" in url:
            title_element = soup.find("span", id="productTitle")
            if title_element:
                title = title_element.text.strip()
            price_element = soup.find("span", class_=re.compile(r"a-price-whole"))
            if price_element:
                price = price_element.text.strip()
            image_element = soup.find("img", id="landingImage")
            if image_element:
                image_url = image_element["src"]

        return {"title": title, "price": price, "image_url": image_url}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"Error parsing product details: {e}")
        return None

@app.route("/")
def index():
    return render_template("index.html", products=products, categories=categories)

@app.route("/product_generator", methods=["GET", "POST"])