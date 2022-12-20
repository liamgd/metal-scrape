import dataclasses
import json
import re
from multiprocessing import Pool
from typing import Any, Dict, Generator, List

import bs4
import requests

WEIGHT_RE = r'^\d*\.?\d*(?= lb$)'


@dataclasses.dataclass
class ProductInfo:
    index: int
    size: str
    desc: str
    product_id: str
    length_skuids: Dict[int, str]
    base_weight: float


@dataclasses.dataclass
class ProductVariation:
    product: ProductInfo
    length: int
    price: float


class DataclassEncoder(json.JSONEncoder):
    def default(self, object: Any):
        if dataclasses.is_dataclass(object):
            return dataclasses.asdict(object)
        return super().default(object)


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
            int(tag.text[:-4]): tag['data-skuid']
            for tag in length_options
            if tag.has_attr('data-skuid')
        }

        yield ProductInfo(
            index, size, desc, product_id, length_skuids, base_weight
        )


def get_product_variation(
    product: ProductInfo, length: int, quantity: int = 1
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
    product_variation = ProductVariation(product, length, price)
    return product_variation


def get_all_product_variations(url: str) -> List[ProductVariation]:
    products = scrape_products(url)
    args_list = [
        (product, length)
        for product in products
        for length in product.length_skuids
    ][:20]
    with Pool() as pool:
        variations = pool.starmap(get_product_variation, args_list)
    return variations


def main() -> None:
    url = 'https://www.metalsdepot.com/steel-products/steel-angle'
    variations = get_all_product_variations(url)
    json.dump()


if __name__ == '__main__':
    main()
