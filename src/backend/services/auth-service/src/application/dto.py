from domain.value_objects import Currency, AccountType

from typing import Any

from pydantic import ConfigDict, dataclasses


@dataclasses.dataclass(config=ConfigDict(from_attributes=True))
class AccountBalanceDTO:
    amount: float
    currency: Currency


@dataclasses.dataclass(config=ConfigDict(from_attributes=True))
class AllAccountBalancesDTO:
    all_account_balances: list["AccountBalanceDTO"]


@dataclasses.dataclass
class UserLogAndPassDTO:
    login: str
    password: str


@dataclasses.dataclass(config=ConfigDict(from_attributes=True))
class TypesOfAccountDTO:
    id: int
    type: AccountType


@dataclasses.dataclass
class AccountBalanceAndTypesOfAccountDTO(AccountBalanceDTO):
    used_type_of_account: list["TypesOfAccountDTO"]


@dataclasses.dataclass
class GetDataFromCacheDTO(AccountBalanceAndTypesOfAccountDTO):
    pass


@dataclasses.dataclass
class SaveDataToCacheDTO:
    pass


@dataclasses.dataclass
class DataForAddToWebServiceDTO:
    data: dict[str, Any]
