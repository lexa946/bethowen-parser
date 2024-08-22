from bs4 import Tag


class Schema(dict):
    def __init__(self):
        super(Schema, self).__init__()

    @classmethod
    def from_tag(cls, tag: Tag) -> "Schema":
        schema = cls()

        list_categories_tags = tag.select(".ixi-nav__second-level")
        for list_categories_tag in list_categories_tags:
            list_categories = ListCategories.from_tag(list_categories_tag)
            schema[list_categories.title] = list_categories
        return schema


class ListCategories(list):
    """
        Список категорий
    """

    def __init__(self):
        super(ListCategories, self).__init__()
        self.title = None
        self.href = None

    @classmethod
    def from_tag(cls, tag: Tag) -> "ListCategories":
        """
            Дополнительный конструктор списка категорий.
        :param tag: bs4 тег самого списка категории
        """
        list_categories = cls()
        title_tag = tag.select_one(".ixi-nav__title a")
        list_categories.title = title_tag.text
        list_categories.href = title_tag.get("href")
        category_tags = tag.select(".ixi-nav__third-level a")
        list_categories.extend(
            Category.from_tag(category_tag) for category_tag in category_tags
        )

        return list_categories

    def __repr__(self):
        return f"<ListCategories {self.title}>"


class Category:
    """
        Категория товара
    """

    def __init__(self, title, href):
        self.title = title
        self.href = href

    @classmethod
    def from_tag(cls, tag: Tag) -> "Category":
        """
            Дополнительный конструктор категории.
        :param tag: bs4 тег самой категории
        """
        title = tag.get("title", "Undefind")
        href = tag.get("href", "Undefind")
        return cls(title, href)

    def __repr__(self):
        return f"<Category {self.title}>"
