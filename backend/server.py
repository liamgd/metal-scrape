import json
from dataclasses import dataclass
from typing import Optional

from app import DataclassEncoder, SpecificProduct, SpecificProducts, load_all

import flask

app = flask.Flask(__name__)


@dataclass
class Global:
    specific_products: Optional[SpecificProducts]


g = Global(None)


@app.route('/')
def index():
    return flask.send_from_directory('../client/public', 'index.html')


@app.route('/<path:path>')
def route(path):
    return flask.send_from_directory('../client/public', path)


@app.route('/products')
def api_specific_products():
    args = flask.request.args
    sort_by = args.get('sort', 'index')
    sort_dir = args.get('sortdir', 'ascending')
    if (
        sort_by not in SpecificProduct.__dataclass_fields__
        or sort_dir not in ('ascending', 'descending')
    ):
        return ''

    ascending = sort_dir == 'ascending'
    sorted_specific_products = g.specific_products.sorted(sort_by, ascending)

    specific_products_json = json.dumps(
        sorted_specific_products, cls=DataclassEncoder
    )
    return specific_products_json


def init() -> None:
    product_bundles = load_all()
    g.specific_products = SpecificProducts(product_bundles)


def main() -> None:
    with app.app_context():
        init()
    app.run(debug=True)


if __name__ == '__main__':
    main()
