from domain.entities import TypeOfAccount, AccountBalance, User
from domain.value_objects import Currency

from application.interfaces.repositories import (
    AccountBalanceRepositoryProtocol,
    UserRepositoryProtocol,
)
from application.interfaces.other_interfaces import (
    CacheProtocol,
    SerializationMapperProtocol,
    HttpApiProtocol,
)
from application.dto import (
    AccountBalanceDTO,
    AllAccountBalancesDTO,
    UserLogAndPassDTO,
    GetDataFromCacheDTO,
    SaveDataToCacheDTO,
    DataForAddToWebServiceDTO,
    AccountBalanceAndTypesOfAccountDTO,
)

from typing_extensions import Any
from datetime import datetime

"""
По хорошему, конечно надо разделить классы с использованием User
и AccountBalance репозиториев на разные файлы
"""


class UserUseCase:
    def __init__(self, user_repo: UserRepositoryProtocol):
        self.repo = user_repo


# ***********************************************************************************************************************


class GetUserUseCase(UserUseCase):
    async def __call__(self, user_id: int) -> UserLogAndPassDTO:
        user: User | None = await self.repo.get_user(user_id)

        if not user:
            raise ValueError(f"Пользователь с id - {user_id} не найден")

        return UserLogAndPassDTO(login=user.login, password=user.password)


class GetAllUsersUseCase(UserUseCase):
    pass


class AddUserUseCase(UserUseCase):
    async def __call__(self, user_login: str, user_pass: str) -> None:
        # Создаю entities юзер, но все поля кроме логина и пароля, я заполняю мусором,
        # потому что не додумался в самом начале в entities поставь в полях None
        user: User = User(
            id=-1,
            login=user_login,
            password=user_pass,
            when_reg=datetime.now(),
            types_of_account=[],
        )
        await self.repo.add_user(user)


class OpenTypeOfAccountWithUserUseCase(UserUseCase):
    async def __call__(self, user_id: int, type_of_account: TypeOfAccount) -> None:
        # 1. Получаем пользователя
        user_for_open_type_of_account: User | None = await self.repo.get_user(user_id)

        if not user_for_open_type_of_account:
            raise ValueError(f"Пользователь c id - {user_id} не найден")

        # 2. Применяем бизнес-логику (Domain)
        user_for_open_type_of_account.open_account(type_of_account)

        # 3. Сохраняем
        await self.repo.save(user_for_open_type_of_account)


# -----------------------------------------------------------------------------------------------------------------------


class AccountBalanceUseCase:
    def __init__(self, account_balance_repo: AccountBalanceRepositoryProtocol):
        self.repo = account_balance_repo


# ***********************************************************************************************************************


class GetAccountBalanceUseCase(AccountBalanceUseCase):
    async def __call__(
        self, user_id: int, type_of_account: TypeOfAccount
    ) -> AccountBalanceDTO:
        account_balance: (
            AccountBalance | None
        ) = await self.repo.get_account_balance_by_user_id_and_type_of_account(
            user_id, type_of_account
        )

        if not account_balance:
            raise ValueError(
                f"Баланс для счёта {type_of_account.type} пользователя не найден"
            )

        return AccountBalanceDTO(
            amount=account_balance.amount, currency=account_balance.currency
        )


class GetAllAccountBalancesUseCase(AccountBalanceUseCase):
    async def __call__(
        self, user_id: int
    ) -> list[AccountBalanceAndTypesOfAccountDTO] | AllAccountBalancesDTO:
        account_balances: (
            list[AccountBalance] | Any
        ) = await self.repo.get_all_account_balances_by_user_id(user_id)

        if not account_balances:
            raise ValueError(
                f"Балансы всех счетов пользователя c id - {user_id} не найдены"
            )

        # Понятно дело, что здесь не должно быть преобразование к типам,
        # но так как возвращаем не AccountBalance, то надо преобразовывать
        return [
            AccountBalanceAndTypesOfAccountDTO(
                amount=float(account_balance.amount),
                currency=Currency(account_balance.currency),
                used_type_of_account=[],
            )
            for account_balance in account_balances
        ]

        # По-хорошему должно возвращать вот это дто, но для облегчения я буду возвращать не его
        # return AllAccountBalancesDTO(
        #     all_account_balances =
        #     [
        #         AccountBalanceDTO(
        #             amount=account_balance.amount,
        #             currency=account_balance.currency
        #         )
        #         for account_balance in account_balances
        #     ]
        # )


class TransferBalanceUseCase(AccountBalanceUseCase):
    async def __call__(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: float,
        type_of_account: TypeOfAccount,
    ) -> None:
        # 1. Получаем балансы
        sender_balance: (
            AccountBalance | None
        ) = await self.repo.get_account_balance_by_user_id_and_type_of_account(
            from_user_id, type_of_account
        )
        receiver_balance: (
            AccountBalance | None
        ) = await self.repo.get_account_balance_by_user_id_and_type_of_account(
            to_user_id, type_of_account
        )

        if not sender_balance or not receiver_balance:
            raise ValueError(
                f"Баланс отправителя - {sender_balance} или получателя - {receiver_balance} не найден"
            )

        # 2. Применяем бизнес-логику (Domain)
        sender_balance.debiting_balance(amount)
        receiver_balance.deposit_to_balance(amount)

        # 3. Сохраняем
        await self.repo.save(sender_balance)
        await self.repo.save(receiver_balance)


# -----------------------------------------------------------------------------------------------------------------------


class CacheUseCase:
    def __init__(
        self, cache: CacheProtocol, serialization_mapper: SerializationMapperProtocol
    ):
        self.cache_client = cache
        self.serialization_mapper = serialization_mapper


# ***********************************************************************************************************************


class GetDataFromCacheUseCase(CacheUseCase):
    """
    Use case for retrieving a data from the cache.
    """

    async def __call__(self, key: str) -> GetDataFromCacheDTO | None | Any:
        cached_data: dict[str, Any] | None = await self.cache_client.hgetall(key)

        if cached_data:
            return cached_data
            # По-хорошему должно возвращать GetDataFromCacheDTO, но для облегчения я буду возвращать не его
            # return self.serialization_mapper.from_dict(cached_data)

        return None


class SaveDataToCacheUseCase(CacheUseCase):
    """
    Use case for saving a something to the cache.
    """

    async def __call__(self, key: str, data_dto: SaveDataToCacheDTO) -> None:
        await self.cache_client.set(key, self.serialization_mapper.to_dict(data_dto))


# -----------------------------------------------------------------------------------------------------------------------


class HttpApiUseCase:
    def __init__(
        self,
        http_api: HttpApiProtocol,
        serialization_mapper: SerializationMapperProtocol,
    ):
        self.http_api = http_api
        self.serialization_mapper = serialization_mapper


# ***********************************************************************************************************************


class GetDataFromWebServiceUseCase(HttpApiUseCase):
    """
    Use case for retrieving a something from the web-service.
    """

    async def __call__(self, params: str) -> Any:
        http_api_data: Any = await self.http_api.get(params)
        return http_api_data


class AddDataToWebServiceUseCase(HttpApiUseCase):
    """
    Use case for add a something to the web-service.
    """

    async def __call__(self, params: str, data_dto: DataForAddToWebServiceDTO) -> None:
        await self.http_api.post(params, self.serialization_mapper.to_dict(data_dto))
