import re

from bs4 import BeautifulSoup
from .schema import Schema


def get_soup(method):
    """
        Обертка для методов парсера, чтобы каждый раз не прописывать создание супа
    :param method: метод декорирования
    """

    def _wrapper(cls, html: str):
        soup = BeautifulSoup(html, features="lxml")
        return method(cls, soup)

    return _wrapper


class HHHtmlParser:
    """
        Парсер необходимых данных из самого HTML
    """

    @classmethod
    @get_soup
    def get_schema(cls, soup: BeautifulSoup) -> Schema:
        """
            Получаем схему товаров из HTML
        """
        schema_tag = soup.select_one("ul.ixi-nav__sub-menu.masonry")
        return Schema.from_tag(schema_tag)

    @classmethod
    @get_soup
    def get_product_ids(cls, soup: BeautifulSoup) -> [str, ...]:
        """
            Получаем все ID товаров со страницы
        """
        section_tags = soup.select(".bth-products-list-container section")
        product_ids = [tag.get("data-product-id", "") for tag in section_tags]
        return product_ids


    @classmethod
    @get_soup
    def get_end_page(cls, soup: BeautifulSoup) -> int:
        """
            Получаем номер последней страницы
        """
        nums_tag = soup.select_one(".nums")
        if nums_tag:
            nums = re.findall(r"\d+", nums_tag.text)
            return max(int(num) for num in nums )
        else:
            return 1