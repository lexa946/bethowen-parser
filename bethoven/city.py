



class City:
    def __init__(self, id_, name, region):
        self.id_ = id_
        self.name = name
        self.region = region

    @classmethod
    def from_dict(cls, dict_: dict):
       return cls(
           id_=dict_.get("id", ""),
           name=dict_.get("name", ""),
           region=dict_.get("region", ""),
       )

    def __repr__(self):
        return f"<City {self.name}>"