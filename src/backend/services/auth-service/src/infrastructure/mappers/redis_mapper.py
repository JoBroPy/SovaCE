from application.dto import GetDataFromCacheDTO

from typing import Any


class RedisCacheMapper:
    @staticmethod
    def to_dict(dto) -> dict[str, Any]:
        return {"": dto}

    @staticmethod
    def from_dict(data: dict[str, Any]):
        return GetDataFromCacheDTO(
            amount=data["amount"],
            currency=data["currency"],
            used_type_of_account=data["used_type_of_account"],
        )
