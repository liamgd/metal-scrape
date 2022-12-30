import json
from dataclasses import dataclass
from typing import Optional

import flask

from .app import DataclassEncoder, SpecificProduct, SpecificProducts, load_all
from .data import materials, shapes

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

    filters = {
        'lengthLower': args.get('lengthLower', None),
        'lengthUpper': args.get('lengthUpper', None),
        'poundsPerFootLower': args.get('poundsPerFootLower', None),
        'poundsPerFootUpper': args.get('poundsPerFootUpper', None),
        'priceLower': args.get('priceLower', None),
        'priceUpper': args.get('priceUpper', None),
        'pricePerFootLower': args.get('pricePerFootLower', None),
        'pricePerFootUpper': args.get('pricePerFootUpper', None),
        'pricePerPoundLower': args.get('pricePerPoundLower', None),
        'pricePerPoundUpper': args.get('pricePerPoundUpper', None),
    }

    filter_materials_string = args.get('materials')
    if filter_materials_string is not None:
        filter_materials = filter_materials_string.split(',')
    else:
        filter_materials = None
    filter_shapes_string = args.get('shapes')
    if filter_shapes_string is not None:
        filter_shapes = filter_shapes_string.split(',')
    else:
        filter_shapes = None

    ascending = sort_dir == 'ascending'
    batch_index = int(args.get('page', 0))
    sorted_specific_products = g.specific_products.search(
        sort_by,
        ascending,
        filter_materials,
        filter_shapes,
        filters,
        batch_index,
    )

    specific_products_json = json.dumps(
        sorted_specific_products, cls=DataclassEncoder
    )
    return specific_products_json


@app.route('/materials')
def api_materials():
    materials_json = json.dumps(materials)
    return materials_json


@app.route('/shapes')
def api_shapes():
    shapes_json = json.dumps(shapes)
    return shapes_json


def init() -> None:
    product_bundles = load_all()
    g.specific_products = SpecificProducts(product_bundles)


def main() -> None:
    with app.app_context():
        init()
    app.run(debug=True, host='0.0.0.0')


if __name__ == '__main__':
    main()
