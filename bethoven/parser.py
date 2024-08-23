import functools

import requests
import random

from tqdm import tqdm

from .html_parser import HHHtmlParser
from .city import City
from .product import Offer, Product

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

PROXIES = [
    {
        'https': 'http://Io2Ar8:iN20YYFn5r@109.248.12.192:1050',
    },

    {
        'https': 'http://Io2Ar8:iN20YYFn5r@46.8.17.237:1050',
    },

    {
        'https': 'http://Io2Ar8:iN20YYFn5r@109.248.12.55:1050',
    },

    {
        'https': 'http://Io2Ar8:iN20YYFn5r@46.8.192.11:1050',
    },

    {
        'https': 'http://Io2Ar8:iN20YYFn5r@46.8.22.2:1050',
    },

    {
        'https': 'http://Io2Ar8:iN20YYFn5r@46.8.22.201:1050',
    },

    {
        'https': 'http://Io2Ar8:iN20YYFn5r@212.115.49.28:1050',
    },

    {
        'https': 'http://Io2Ar8:iN20YYFn5r@109.248.142.144:1050',
    },

    {
        'https': 'http://Io2Ar8:iN20YYFn5r@45.11.21.40:1050',
    },

    {
        'https': 'http://Io2Ar8:iN20YYFn5r@188.130.128.142:1050',
    },

]


def set_random_proxy(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if PROXIES:
            self._session.proxies.update(random.choice(PROXIES))
        return method(self, *args, **kwargs)

    return wrapper


class Parser:
    main_url = "https://www.bethowen.ru/"

    def __init__(self, max_connections=3):
        self._threads = []
        self._executor = ThreadPoolExecutor(max_workers=max_connections)
        self._session = requests.session()
        self._set_session_param()
        self.city = None
        self._session.proxies.update()

    def _test_url(self, url, method, json=None, data=None, params=None):
        response = self._session.request(method, url, json=json, data=data, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text)
        return response, soup

    @set_random_proxy
    def get_schema(self):
        """
            Получаем схему по сайту.
        :return:
        """
        response = self._session.get(self.main_url, )
        response.raise_for_status()
        return HHHtmlParser.get_schema(html=response.text)

    def _set_session_param(self) -> None:
        """
            Установка базовых параметров для сессии requests
        """
        self._session.verify = False
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36",
        }
        self._session.trust_env = False

    def checkout(self):
        response = self._session.get(self.main_url + "api/local/v1/orders/checkout/init")
        response.raise_for_status()
        return response.json()

    @set_random_proxy
    def get_products_list(self, category_href: str) -> [Product, ...]:
        """
            Получаем список продуктов по категории
        :return:
        """
        self._threads = []
        products = []
        end_page = self._get_end_page(category_href)

        for page_num in range(1, end_page + 1):
            self._threads.append(self._executor.submit(self._get_products_from_page, category_href, page_num))
            # if page_num == 3:
            #     break

        for thread in tqdm(as_completed(self._threads), total=len(self._threads)):
            products.extend(thread.result())

        return products

    @set_random_proxy
    def _get_products_from_page(self, category_href: str, page_num: int) -> [Product, ...]:
        products = []
        response = self._session.get(self.main_url + category_href, params={
            "PAGEN_1": page_num,
        })
        response.raise_for_status()
        products_ids = HHHtmlParser.get_product_ids(html=response.text)
        products_list = self._get_products_list_from_api(products_ids)
        products.extend(products_list)
        return products

    def _get_end_page(self, category_href: str) -> int:
        response = self._session.get(self.main_url + category_href, params={
            "PAGEN_1": 1,
        })
        response.raise_for_status()
        return HHHtmlParser.get_end_page(html=response.text)

    def _get_products_list_from_api(self, products_ids: [str, ...]) -> [Product, ...]:
        """
            Получаем список продувтов из API
        :param products_ids:
        :return:
        """
        response = self._session.get(self.main_url + "api/local/v1/catalog/list", params={
            "limit": 20,
            "sort_type": "popular",
            "id[]": products_ids
        })
        response.raise_for_status()
        products = [
            Product.from_dict(product_dict) for product_dict in response.json().get("products", [])
        ]
        for product in products:
            product.offers = [self.get_offer_details(offer_id) for offer_id in product.current_offer_ids]

        return products

    def get_product_details(self, product_id: str) -> Product:
        """
            Получить полную детальную информацию по продукту
        :param product_id: ID продукта
        :return:
        """
        # print(product_id)
        response = self._session.get(self.main_url + f"/api/local/v1/catalog/products/{product_id}/details")
        response.raise_for_status()
        product = Product.from_dict(response.json())
        product.offers = [self.get_offer_details(offer_id) for offer_id in product.current_offer_ids]
        return product

    def get_offer_details(self, offer_id: str) -> Offer:
        """
            Получаем полную дедальную информацию по оферу
        :param offer_id: ID офера
        :return:
        """
        response = self._session.get(self.main_url + f"api/local/v1/catalog/offers/{offer_id}/details")
        response.raise_for_status()
        return Offer.from_dict(response.json())

    def get_cities(self, name: str) -> list[City]:
        """
            Возвращает все найденные города
        :param name: Название, либо часть названия города
        :return:
        """

        response = self._session.get(self.main_url + "api/local/v1/cities/search", params={
            "city_type": "all",
            "term": name,
        }, headers={"Accept": "application/json"})
        response.raise_for_status()
        return [City.from_dict(city) for city in response.json().get("cities", [])]

    def set_city(self, city: City):
        """
            Ставим
        :param city_id:
        :return:
        """
        response = self._session.post(self.main_url + "api/local/v1/users/location",
                                      json={
                                          "location_id": city.id_,
                                      })
        response.raise_for_status()
        self.city = city
