import dataclasses
import json
import os
import re
from multiprocessing import Pool
from typing import Any, Dict, Generator, List, Optional, Tuple

import bs4
import dacite
import requests
import shortuuid

WEIGHT_RE = r'^\d*\.?\d*(?= lb$)'


@dataclasses.dataclass
class ProductInfo:
    uuid: str
    product_id: str
    index: int
    size: str
    desc: str
    length_skuids: Dict[str, str]
    base_weight: float


@dataclasses.dataclass
class ProductVariation:
    parent_uuid: str
    length: int
    price: float


@dataclasses.dataclass
class SpecificProduct:
    uuid: str
    product_id: str
    index: int
    size: str
    desc: str
    base_weight: float
    length: int
    price: float
    price_per_foot: float
    price_per_pound: float


class DataclassEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def scrape_products(url: str) -> Generator[ProductInfo, None, None]:
    response = requests.get(url)
    content = response.content
    site = bs4.BeautifulSoup(content, 'html5lib')
    products: List[bs4.element.Tag] = list(
        site.find_all('div', attrs={'class': 'product-row'})
    )

    for index, product in enumerate(products, 1):
        info = tuple(
            product.find('div', class_='product-size').stripped_strings
        )
        if len(info) != 2:
            continue
        size, desc = info
        base_weight_text = product.find(
            'div', class_='product-base-weight'
        ).text
        base_weight_match = re.search(WEIGHT_RE, base_weight_text)
        if base_weight_match is None:
            continue
        base_weight = float(base_weight_match.group())
        product_id = product['data-product-id']
        length_select = product.find('select', class_='length-select')
        length_options: List[bs4.element.Tag] = list(
            length_select.find_all('option')
        )
        length_skuids = {
            tag.text.removesuffix(' Ft.'): tag['data-skuid']
            for tag in length_options
            if tag.has_attr('data-skuid') and tag.text.endswith(' Ft.')
        }

        uuid = shortuuid.uuid()
        yield ProductInfo(
            uuid, product_id, index, size, desc, length_skuids, base_weight
        )


def get_product_variation(
    product: ProductInfo, length: str, quantity: int = 1
) -> ProductVariation:
    if length not in product.length_skuids:
        raise ValueError(
            f'Length {length} not in valid lengths {product.length_skuids}'
        )
    payload = {
        'request': 'metals.getPrice',
        'data[product_id]': product.product_id,
        'data[qty]': quantity,
        'data[sku_id]': product.length_skuids[length],
    }
    url = 'https://www.metalsdepot.com/system/modrequest'
    response = requests.post(url, payload)
    if response.status_code != 200:
        raise ValueError(
            f'Response unsuccessful with status code {response.status_code}'
        )
    content = response.content.decode('ascii')
    price = float(content)
    product_variation = ProductVariation(product.uuid, int(length), price)
    return product_variation


def get_all_product_variations(
    products: List[ProductInfo], limit: Optional[int] = None
) -> List[ProductVariation]:
    args_list = [
        (product, length)
        for product in products
        for length in product.length_skuids
    ]
    if limit is not None:
        args_list = args_list[:limit]
    with Pool() as pool:
        variations = pool.starmap(get_product_variation, args_list)
    return variations


def save(path: Optional[str] = None) -> None:
    if path is None:
        path = os.path.expanduser('~')
    products_path = os.path.join(path, 'products.json')
    variations_path = os.path.join(path, 'variations.json')

    url = 'https://www.metalsdepot.com/steel-products/steel-angle'
    products: List[ProductInfo] = list(scrape_products(url))
    with open(products_path, 'w') as file:
        json.dump(products, file, cls=DataclassEncoder, indent=4)

    variations = get_all_product_variations(products)
    with open(variations_path, 'w') as file:
        json.dump(variations, file, cls=DataclassEncoder, indent=4)


def load(
    path: Optional[str] = None,
) -> Tuple[List[ProductInfo], List[ProductVariation]]:
    if path is None:
        path = os.path.expanduser('~')
    products_path = os.path.join(path, 'products.json')
    variations_path = os.path.join(path, 'variations.json')

    with open(products_path, 'r') as file:
        product_dicts = json.load(file)
        products = [
            dacite.from_dict(ProductInfo, product_dict)
            for product_dict in product_dicts
        ]

    with open(variations_path, 'r') as file:
        variation_dicts = json.load(file)
        variations = [
            dacite.from_dict(ProductVariation, variation_dict)
            for variation_dict in variation_dicts
        ]

    return products, variations


def get_specific_product(
    variation: ProductVariation, products: List[ProductInfo]
) -> SpecificProduct:
    uuid = variation.parent_uuid
    product = next((p for p in products if p.uuid == uuid))
    price_per_foot = variation.price / variation.length
    price_per_pound = variation.price / (
        product.base_weight * variation.length
    )
    specific = SpecificProduct(
        uuid,
        product.product_id,
        product.index,
        product.size,
        product.desc,
        product.base_weight,
        variation.length,
        variation.price,
        price_per_foot,
        price_per_pound,
    )
    return specific


class SpecificProducts:
    def __init__(
        self, products: List[ProductInfo], variations: List[ProductVariation]
    ) -> List[SpecificProduct]:
        self.specific_products = [
            get_specific_product(variation, products)
            for variation in variations
        ]
        self.sort_cache = {}

    def sorted(
        self,
        attribute: str,
        ascending: bool,
        batch_index: int = 0,
        batch_limit: int = 20,
    ) -> List[SpecificProduct]:
        if (attribute, ascending) in self.sort_cache:
            indices = self.sort_cache[(attribute, ascending)]
            sorted_specific_products = [
                self.specific_products[i]
                for i in indices[batch_index : batch_index + batch_limit]
            ]
            return sorted_specific_products

        order = ['index', 'length', 'price', 'base_weight']
        if attribute in order:
            order.remove(attribute)
        order.insert(0, attribute)
        decorated: List[Tuple[Any, Any, Any, Any, SpecificProduct, int]] = [
            tuple(getattr(specific_product, attr) for attr in order)
            + (specific_product, index)
            for index, specific_product in enumerate(self.specific_products)
        ]
        decorated.sort(reverse=not ascending)
        sorted_specific_products = [
            entry[-2]
            for entry in decorated[batch_index : batch_index + batch_limit]
        ]
        indices = [entry[-1] for entry in decorated]
        self.sort_cache[(attribute, ascending)] = indices
        return sorted_specific_products


def main() -> None:
    products, variations = load()
    specific_products = SpecificProducts(products, variations)
    print(specific_products.specific_products)


if __name__ == '__main__':
    main()
