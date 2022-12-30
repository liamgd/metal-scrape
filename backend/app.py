import dataclasses
import json
import os
import re
from multiprocessing import Pool
from typing import Any, Dict, Generator, List, Literal, Optional, Tuple

import bs4
import dacite
import requests
import shortuuid

from .data import URLS

WEIGHT_RE = r'^\d*\.?\d*(?= lb$)'
DATA_DIR = 'metalscrape'


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
    product_id: str
    index: int
    material: str
    shape: str
    size: str
    desc: str
    base_weight: float
    length: int
    price: float
    price_per_foot: float
    price_per_pound: float

    def __gt__(self, _: 'SpecificProduct') -> Literal[False]:
        return False


ProductBundles = Dict[
    Tuple[str, str], Tuple[List[ProductInfo], List[ProductVariation]]
]


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


def save(url: str, file_name: str, path: Optional[str] = None) -> None:
    if path is None:
        path = os.path.join(os.path.expanduser('~'), DATA_DIR)
    products_path = os.path.join(path, file_name + '.products.json')
    variations_path = os.path.join(path, file_name + '.variations.json')

    products: List[ProductInfo] = list(scrape_products(url))
    with open(products_path, 'w') as file:
        json.dump(products, file, cls=DataclassEncoder, indent=4)

    variations = get_all_product_variations(products)
    with open(variations_path, 'w') as file:
        json.dump(variations, file, cls=DataclassEncoder, indent=4)


def format_file_name(text: str) -> str:
    return text.lower().replace(' ', '_')


def unformat_file_name(text: str) -> str:
    return text.replace('_', ' ').title()


def save_all(
    urls: Dict[Tuple[str, str], str], path: Optional[str] = None
) -> None:
    for index, ((material, shape), url) in enumerate(urls.items(), 1):
        file_name = format_file_name(material) + '.' + format_file_name(shape)
        save(url, file_name, path)
        print(f'`Saved` {index} out of {len(urls)}: {material}, {shape}')


def load(
    file_name: str,
    path: str,
) -> Tuple[List[ProductInfo], List[ProductVariation]]:
    products_path = os.path.join(path, file_name + '.products.json')
    variations_path = os.path.join(path, file_name + '.variations.json')
    if not os.path.exists(products_path):
        raise FileNotFoundError(
            f'Products JSON file not found at {products_path}'
        )
    if not os.path.exists(variations_path):
        raise FileNotFoundError(
            f'Variation JSON file not found at {variations_path}'
        )

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


def load_all(
    path: Optional[str] = None,
) -> ProductBundles:
    if path is None:
        path = os.path.join(os.path.expanduser('~'), DATA_DIR)
    out: ProductBundles = {}
    file_names = os.listdir(path)
    for file_name in file_names:
        file_path = os.path.join(path, file_name)
        if not os.path.isfile(file_path):
            print(f'Skipping path {file_path}: not a file.')
            continue
        if file_name.count('.') != 3:
            print(f'Skipping path {file_path}: improperly formatted file name')
            continue
        material, shape, data_type, ending = file_name.split('.')
        if ending != 'json':
            print(f'Skipping path {file_path}: not a JSON file.')
            continue
        material = unformat_file_name(material)
        shape = unformat_file_name(shape)
        if data_type == 'products':
            out[(material, shape)] = load(
                file_name.removesuffix('.products.json'), path
            )
    return out


def stitch_specific_product(
    product: ProductInfo,
    variation: ProductVariation,
    material: str,
    shape: str,
) -> SpecificProduct:
    price_per_foot = variation.price / variation.length
    price_per_pound = variation.price / (
        product.base_weight * variation.length
    )
    specific = SpecificProduct(
        product.uuid,
        product.index,
        material,
        shape,
        product.size,
        product.desc,
        product.base_weight,
        variation.length,
        variation.price,
        price_per_foot,
        price_per_pound,
    )
    return specific


def get_specific_product(
    variation: ProductVariation,
    products: List[ProductInfo],
    material: str,
    shape: str,
) -> SpecificProduct:
    uuid = variation.parent_uuid
    product = next((p for p in products if p.uuid == uuid))
    specific = stitch_specific_product(product, variation, material, shape)
    return specific


def get_all_specific_products(
    product_bundles: ProductBundles,
) -> List[SpecificProduct]:
    specific_products: List[SpecificProduct] = []
    for (material, shape), (products, variations) in product_bundles.items():
        products_dict = {product.uuid: product for product in products}
        for variation in variations:
            product = products_dict[variation.parent_uuid]
            specific = stitch_specific_product(
                product, variation, material, shape
            )
            specific_products.append(specific)
    return specific_products


class SpecificProducts:
    def __init__(
        self, product_bundles: ProductBundles
    ) -> List[SpecificProduct]:
        self.specific_products = get_all_specific_products(product_bundles)
        self.sort_cache = {}

    def search(
        self,
        attribute: str,
        ascending: bool,
        materials: Optional[List[str]],
        shapes: Optional[List[str]],
        filters: Dict[str, str],
        batch_index: int = 0,
        batch_limit: int = 20,
    ) -> List[SpecificProduct]:
        if (attribute, ascending) in self.sort_cache:
            indices = self.sort_cache[(attribute, ascending)]
            sorted_specific_products = [
                self.specific_products[index] for index in indices
            ]
        else:
            order = ['index', 'length', 'price', 'base_weight']
            if attribute in order:
                order.remove(attribute)
            order.insert(0, attribute)
            decorated: List[
                Tuple[Any, Any, Any, Any, SpecificProduct, int]
            ] = [
                tuple(getattr(specific_product, attr) for attr in order)
                + (specific_product, index)
                for index, specific_product in enumerate(
                    self.specific_products
                )
            ]
            decorated.sort(reverse=not ascending)
            sorted_specific_products = [entry[-2] for entry in decorated]
            indices = [entry[-1] for entry in decorated]
            self.sort_cache[(attribute, ascending)] = indices

        def filter_func(specific_product: SpecificProduct) -> bool:
            return not (
                (
                    materials is not None
                    and specific_product.material not in materials
                )
                or (
                    shapes is not None and specific_product.shape not in shapes
                )
                or (
                    filters['lengthLower'] is not None
                    and specific_product.length < float(filters['lengthLower'])
                )
                or (
                    filters['lengthUpper'] is not None
                    and specific_product.length > float(filters['lengthUpper'])
                )
                or (
                    filters['poundsPerFootLower'] is not None
                    and specific_product.base_weight
                    < float(filters['poundsPerFootLower'])
                )
                or (
                    filters['poundsPerFootUpper'] is not None
                    and specific_product.base_weight
                    > float(filters['poundsPerFootUpper'])
                )
                or (
                    filters['priceLower'] is not None
                    and specific_product.price < float(filters['priceLower'])
                )
                or (
                    filters['priceUpper'] is not None
                    and specific_product.price > float(filters['priceUpper'])
                )
                or (
                    filters['pricePerFootLower'] is not None
                    and specific_product.price_per_foot
                    < float(filters['pricePerFootLower'])
                )
                or (
                    filters['pricePerFootUpper'] is not None
                    and specific_product.price_per_foot
                    > float(filters['pricePerFootUpper'])
                )
                or (
                    filters['pricePerPoundLower'] is not None
                    and specific_product.price_per_pound
                    < float(filters['pricePerPoundLower'])
                )
                or (
                    filters['pricePerPoundUpper'] is not None
                    and specific_product.price_per_pound
                    > float(filters['pricePerPoundUpper'])
                )
            )

        filtered_specific_products = list(
            filter(filter_func, sorted_specific_products)
        )
        return filtered_specific_products[
            batch_index * batch_limit : (batch_index + 1) * batch_limit
        ]


def main() -> None:
    save_all(URLS)
    product_bundles = load_all()
    SpecificProducts(product_bundles)


if __name__ == '__main__':
    main()
