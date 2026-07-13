from domain.entities import AccountBalance, User, TypeOfAccount
from domain.value_objects import Currency

from infrastructure.database.models import UsersBalance, Users

from typing import Any
import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError


class SQLAlchemyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


class SQLAlchemyAccountBalanceRepository(SQLAlchemyRepository):
    async def get_account_balance_by_user_id_and_type_of_account(
        self, user_id: int, type_of_account: TypeOfAccount
    ) -> AccountBalance | None:

        stmt = select(UsersBalance).where(
            UsersBalance.user_id == user_id,
            UsersBalance.used_type_of_trade == type_of_account.type,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        # Маппинг: Model → Domain Entity
        # В user надо по-хорошему передавать объект класса User, однако я этим пренебрёг,
        # потому что я нигде не использую данную функцию
        return AccountBalance(
            id=model.id,
            user=model.user_id,  # type: ignore[arg-type]
            currency=Currency(model.currency),
            amount=model.amount,  # type: ignore[arg-type]
        )

    async def get_all_account_balances_by_user_id(
        self, user_id: int
    ) -> list[AccountBalance] | Any:

        stmt = (
            select(UsersBalance)
            .options(selectinload(UsersBalance.user))
            .where(UsersBalance.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        if not models:
            return []
        return models

        # По-хорошему должно возвращать вот эту сущность, но для облегчения я буду возвращать не его
        # return [
        #     AccountBalance(
        #         id=m.id,
        #         user=User(
        #             id=m.user.id,
        #             login=m.user.login,
        #             password=m.user.password,
        #             when_reg=m.user.when_reg,
        #             types_of_account=[]
        #         ),
        #         currency=Currency(m.currency),
        #         amount=m.amount
        #     )
        #     for m in models
        # ]

    async def save(self, account_balance: AccountBalance) -> None:
        # Маппинг: Domain Entity → Model
        model = UsersBalance(
            id=account_balance.id,
            currency=account_balance.currency.value,
            amount=account_balance.amount,
            user_id=account_balance.user.id,
        )
        self.session.add(model)
        await self.session.commit()


class SQLAlchemyUserRepository(SQLAlchemyRepository):
    async def get_user(self, user_id: int) -> User | None:
        pass

    async def get_all_users(self) -> list[User]:
        return list()

    async def add_user(self, user: User) -> None:
        stmt_for_check = select(1).where(Users.login == user.login).limit(1)
        result = await self.session.execute(stmt_for_check)

        if result.first():
            raise Exception(
                "Registration failed: Этот пользователь уже зарегистрирован.\nСтатус код:409"
            )

        try:
            stmt_for_add = insert(Users).values(
                login=user.login,
                password=bcrypt.hashpw(
                    user.password.encode(), bcrypt.gensalt()
                ).decode(),
            )
            await self.session.execute(stmt_for_add)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise Exception(
                f"Пользователь уже существует\nПодробнее: {e}.\nСтатус код:409"
            )

    async def save(self, user: User) -> None:
        pass


# -----Снизу просто изучение SQLAlchemy----------------------------------------------------------------------------------
# async def pro_select(session_factory_for_test: async_sessionmaker[AsyncSession]):
#     async with session_factory_for_test() as session:
#         query = (
#             select(
#                 UsersBalance.what_is,
#                 cast(func.avg(UsersBalance.balance), Integer).label("avg_balance"),
#             )
#             .select_from(UsersBalance)
#             .filter(or_(
#                 UsersBalance.what_is.contains("BTC"),
#                 UsersBalance.what_is.contains("ETH")
#             ))
#             .group_by(UsersBalance.what_is)
#         )
#         print(query.compile(compile_kwargs={"literal_binds": True}))
#         res = await session.execute(query)
#         print(res.all())

# async def select_users_with_condition_relationship(session_factory_for_test: async_sessionmaker[AsyncSession]):
#     async with session_factory_for_test() as session:
#         query = (
#             select(Users)
#             .options(selectinload(Users.balances_eth))
#         )
#         res = await session.execute(query)
#         # for user in res.scalars().all():
#         #     print(user.balances_eth)
#
#         result = res.scalars().all()
#         print(result)

# async def select_users_with_condition_relationship_contains_eager(session_factory_for_test: async_sessionmaker[AsyncSession]):
#     async with session_factory_for_test() as session:
#         query = (
#             select(Users)
#             .join(Users.balances)
#             .options(contains_eager(Users.balances) )
#         )
#         res = await session.execute(query)
#         # for user in res.scalars().all():
#         #     print(user.balances_eth)
#
#         result = res.all()
#         print(result)

# async def add_types_and_balance(session_factory_for_test: async_sessionmaker[AsyncSession]):
#     async with session_factory_for_test() as session:
#         new_type_of_trade = TypesOfTrade(type="Futures")
#
#         balance_1 = await session.get(UsersBalance, 1)
#         balance_1.used_type_of_trade.append(new_type_of_trade)
#
#         await session.commit()

# async def select_balances_with_all_relationships(session_factory_for_test: async_sessionmaker[AsyncSession]):
#     async with session_factory_for_test() as session:
#         query = (
#             select(UsersBalance)
#             .options(joinedload(UsersBalance.user))
#         )
#
#         res = await session.execute(query)
#         result = res.unique().scalars().all()
#         print(result)

# async def main(session_factory):
#     await add_types_and_balance(session_factory)
#     await select_balances_with_all_relationships(session_factory)

# asyncio.run(main(session_factory))

# engine = create_engine(
#     url=os.getenv("DATABASE_URL_SYNC"),
#     echo=False,
#     pool_size=5,
#     max_overflow=10
# )
# session = sessionmaker(engine)

# async def create_tables():
#     async with engine.connect() as conn:
#         # engine.echo = False
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#         # engine.echo = True
#         await conn.commit()
#
# async def insert_data():
#     async with engine.connect() as conn:
#
#         # stmt = """INSERT INTO users (login, password) VALUES
#         #     ('Bob', 'Bob123'),
#         #     ('Alex', 'Alex123');"""
#
#         stmt = insert(Users).values(
#             [
#                 {"login": "bobr", "password": "kur"},
#                 {"login": "volk", "password": "chert"},
#             ]
#         )
#         await conn.execute(stmt)
#         await conn.commit()
#
# async def insert_data_orm():
#     async with session_factory() as session:
#         user_google = Users(login="google", password="google123")
#         user_yandex = Users(login="yandex", password="yandex123")
#         session.add_all([user_google, user_yandex])
#         await session.commit()
#
# async def main():
#     await create_tables()
#     await insert_data_orm()
#     await engine.dispose()  # Хорошая практика: закрыть пул соединений
