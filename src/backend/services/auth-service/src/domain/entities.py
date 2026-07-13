from dataclasses import dataclass
from datetime import datetime

from domain.value_objects import Currency, AccountType


@dataclass
class User:
    id: int
    login: str
    password: str
    when_reg: datetime
    types_of_account: list["TypeOfAccount"]

    # Бизнес-правила (инварианты)
    def open_account(self, type_of_account: "TypeOfAccount") -> None:
        """Добавление в список нового типа счёта"""
        if type_of_account.type in [i.type for i in self.types_of_account]:
            raise ValueError(f"Cчёт {type_of_account.type} уже открыт.")
        elif len(self.types_of_account) == len(Currency):
            raise ValueError("Все счета открыты. Новый счёт открыть невозможно")
        self.types_of_account.append(type_of_account)


@dataclass
class AccountBalance:
    id: int
    user: "User"
    currency: Currency
    amount: float

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Валюты на счёте не может быть отриц. количество")

    # Бизнес-правила (инварианты)
    def debiting_balance(self, amount: float) -> None:
        """Списание с проверкой бизнес-правил"""
        if self.amount < amount <= 0:
            raise ValueError(f"Недостаточно средств. Баланс: {self.amount}")
        self.amount -= amount

    def deposit_to_balance(self, amount: float) -> None:
        """Пополнение с проверкой бизнес-правил"""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        elif amount < self.currency.price_min_deposit:
            raise ValueError(
                f"Сумма пополнения должна "
                f"быть больше или равна минимальной -> {self.currency.price_min_deposit}"
            )
        self.amount += amount


@dataclass
class TypeOfAccount:
    id: int
    type: AccountType
    account_balance: "AccountBalance"
