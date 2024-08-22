class Shop:
    """
        Информация по магазинам
    """

    def __init__(self, id_: str, address: str, subways: [str, ...], availability: str, position: [float, float]):
        self.position = position
        self.availability = availability
        self.subways = subways
        self.address = address
        self.id = id_




    @classmethod
    def from_dict(cls, dict_):
        if "position" in dict_:
            position = [
                float(dict_["position"]["lat"]),
                float(dict_["position"]["long"]),
            ]
        else:
            position = [0, 0]

        availability = dict_["availability"]["text"] if "availability" in dict_ else "Нет"

        subways = [subway["name"] for subway in dict_.get("subways", [])]

        return cls(
            id_=dict_.get("id", ""),
            address=dict_.get("address", ""),
            subways=subways,
            availability=availability,
            position=position,
        )

    def __repr__(self):
        return f"<Shop {self.address}>"
