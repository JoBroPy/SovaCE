from domain.entities import AccountBalance, User, TypeOfAccount

from typing import Protocol, Any


class AccountBalanceRepositoryProtocol(Protocol):
    async def get_account_balance_by_user_id_and_type_of_account(
        self, user_id: int, type_of_account: TypeOfAccount
    ) -> AccountBalance | None: ...

    async def get_all_account_balances_by_user_id(
        self, user_id: int
    ) -> list[AccountBalance] | Any: ...

    async def save(self, account_balance: AccountBalance) -> None: ...


class UserRepositoryProtocol(Protocol):
    async def get_user(self, user_id: int) -> User | None: ...

    async def get_all_users(self) -> list[User]: ...

    async def add_user(self, user: User) -> None: ...

    # async def open_type_of_account_with_user(self, user_id: int, type_of_account: TypeOfAccount) -> None:
    #     ...

    async def save(self, user: User) -> None: ...
