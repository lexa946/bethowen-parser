from .shop import Shop


class Product:
    def __init__(self, id_: str, name: str, description: str, offers: ["Offer", ...], current_offer_ids=None):
        self.description = description
        self.offers = offers
        self.name = name
        self.id_ = id_
        self.current_offer_ids = current_offer_ids or []

    @classmethod
    def from_dict(cls, dict_: dict):
        return cls(
            id_=dict_.get("id", ""),
            name=dict_.get("name", ""),
            description=dict_.get("description", ""),
            offers=[],
            current_offer_ids=[offer['id'] for offer in dict_.get("offers", [])]
        )

    def __repr__(self):
        return f"<Product {self.id_}>"


class Offer:
    """
        Полная информация об оффере
    """

    def __init__(self, id_: str, size: str, retail_price: str, discount_price: str, vendor_code: str,
                 shops: [Shop, ...]):
        self.discount_price = discount_price
        self.retail_price = retail_price
        self.vendor_code = vendor_code
        self.size = size
        self.id = id_
        self.shops = shops

    @classmethod
    def from_dict(cls, dict_: dict) -> "Offer":
        shops = []
        if "availability_info" in dict_:
            for shop_dict in dict_["availability_info"].get("offer_store_amount", []):
                shop = Shop.from_dict(shop_dict)
                shops.append(shop)

        return cls(
            id_=dict_.get("id", ""),
            size=dict_.get("size", ""),
            retail_price=dict_.get("retail_price", ""),
            discount_price=dict_.get("discount_price", ""),
            vendor_code=dict_.get("vendor_code", ""),
            shops=shops
        )

    def __repr__(self):
        return f"<Offer {self.id}>"
