import json
from typing import List

from app import (
    DataclassEncoder,
    ProductInfo,
    ProductVariation,
    get_specific_product,
    load,
)
from flask import Flask, send_from_directory

app = Flask(__name__)

products: List[ProductInfo] = []
variations: List[ProductVariation] = []


@app.route("/")
def index():
    return send_from_directory('../client/public', 'index.html')


@app.route("/<path:path>")
def route(path):
    return send_from_directory('../client/public', path)


@app.route("/products")
def api_specific_products():
    specific_products = [
        get_specific_product(variation, products) for variation in variations
    ]
    specific_products_json = json.dumps(
        specific_products, cls=DataclassEncoder, indent=4
    )
    return specific_products_json


def main() -> None:
    products[:], variations[:] = load()
    app.run(debug=True)


if __name__ == "__main__":
    main()
