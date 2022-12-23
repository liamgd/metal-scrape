import json
from typing import TYPE_CHECKING, List

from app import (
    DataclassEncoder,
    ProductInfo,
    ProductVariation,
    SpecificProduct,
    SpecificProducts,
    load,
)

import flask

app = flask.Flask(__name__)


if TYPE_CHECKING:

    class _g(flask.ctx._AppCtxGlobals):
        products: List[ProductInfo]
        variations: List[ProductVariation]
        specific_products: SpecificProducts

    g = _g()
else:
    g = flask.g


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
    g.products, g.variations = load()
    g.specific_products = SpecificProducts(g.products, g.variations)


def main() -> None:
    with app.app_context():
        init()
    app.run(debug=True)


if __name__ == '__main__':
    main()
