from application.dto import DataForAddToWebServiceDTO

from typing import Any


class HttpApiMapper:
    @staticmethod
    def to_dict(dto) -> dict[str, Any]:
        return {"": dto}

    @staticmethod
    def from_dict(data: dict[str, Any]):
        return DataForAddToWebServiceDTO(data)
