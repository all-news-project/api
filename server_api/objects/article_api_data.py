from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ArticleApiData:
    title: str
    media: str
    url: str
    icon_url: Optional[str]
    publishing_time: Optional[str]

    def convert_to_dict(self) -> dict:
        return asdict(self)
