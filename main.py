import csv
from bethoven import Parser
from configparser import ConfigParser
from loguru import logger

from bethoven.product import Product

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def save_to_csv(products_list: [Product, ...], csv_filename: str, all_shops: bool = False):
    """
        Сохранение списка продуктов в файл csv
    :param products_list: список продуктов
    :param csv_filename: название файла
    """
    with open(csv_filename + ".csv", "w", encoding=CONFIG['Main']['csv_encoding'], newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(['City', 'Code', 'Name', 'Price Retail', 'Price Discount', 'Address', 'Available'])

        for product in products_list:
            for offer in product.offers:
                if CONFIG['Main']['address_tt']:
                    if not all_shops:
                        writer.writerow((
                            CONFIG['Main']['city_name'],
                            offer.vendor_code,
                            product.name,
                            offer.retail_price,
                            offer.discount_price,
                            offer.shops[0].address,
                            offer.shops[0].availability,
                        ))
                    else:
                        for shop in offer.shops:
                            writer.writerow((
                                CONFIG['Main']['city_name'],
                                offer.vendor_code,
                                product.name,
                                offer.retail_price,
                                offer.discount_price,
                                shop.address,
                                shop.availability,
                            ))

    logger.info(f"Файл {csv_filename}.csv создан.")


CONFIG = ConfigParser()
CONFIG.read("config.ini", encoding="UTF-8")
logger.add(CONFIG['Main']['logger_file'])

PARSER = Parser(int(CONFIG['Main'].get('max_connection', 1)))
SCHEMA = PARSER.get_schema()
PRODUCTS = []

if CONFIG['Main']['city_name']:
    cities = PARSER.get_cities(CONFIG['Main']['city_name'])
    if not cities:
        ex_text = f"Город {CONFIG['Main']['city_name']} не найден!"
        logger.error(ex_text)
        raise ValueError(ex_text)
    if len(cities) > 1:
        logger.warning("Найдено больше 1 города.")
        logger.warning("\n".join(
            f"{i}. {city.name}" for i, city in enumerate(cities)
        ))
        city_num = int(input("Выберите необходимый город: "))
        city = cities[city_num]
    else:
        city = cities[0]
    PARSER.set_city(city)
    CONFIG['Main']['city_name'] = city.name
    logger.info(f"Город {city.name} установлен.")

if CONFIG['Main']['show_all_category'] == "True":
    for list_categories in SCHEMA.values():
        for category in list_categories:
            logger.info(f"Категория: {list_categories.title}/{category.title}. href={category.href}")

catalog_href = CONFIG['Main'].get('category_href', 'all_catalogs')

if catalog_href != 'all_catalogs':
    logger.info(f"Парсинг будет по каталогу {catalog_href}")
    PRODUCTS.extend(PARSER.get_products_list(catalog_href))

else:
    logger.info(f"Каталог не указан, парсинг будет по всем категориям.")
    SCHEMA = PARSER.get_schema()
    for schema_key in SCHEMA:
        logger.info(f"Парсинг каталога {SCHEMA[schema_key].title}. href={SCHEMA[schema_key].href}")
        PRODUCTS.extend(PARSER.get_products_list(SCHEMA[schema_key].href))

save_to_csv(PRODUCTS, catalog_href.replace('/', '_') + "_all", all_shops=True)


def filter_address(product: Product):
    address = CONFIG['Main']['address_tt']
    shops_address = []
    for offer in product.offers:
        offer.shops = list(filter(lambda shop: shop.address == address, offer.shops))
        shops_address.extend(
            shop.address for shop in offer.shops
        )
    product.offers = list(filter(lambda offer: offer.shops, product.offers))
    if address in shops_address:
        return True
    return False


if CONFIG['Main']['address_tt']:
    PRODUCTS = list(filter(filter_address, PRODUCTS))
    save_to_csv(PRODUCTS, catalog_href.replace('/', '_') + "_address_filter")

print()
