from dataclasses import dataclass, asdict


@dataclass
class ArticleApiData:
    title: str
    domain: str
    url: str

    def convert_to_dict(self) -> dict:
        return asdict(self)
