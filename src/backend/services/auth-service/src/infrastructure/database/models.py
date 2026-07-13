from sqlalchemy import String, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import datetime
from typing import Annotated

intpk = Annotated[int, mapped_column(primary_key=True, index=True)]
created_at = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]
str_100 = Annotated[str, mapped_column(String(100), unique=True, index=True)]


class Base(DeclarativeBase):
    def __repr__(self):
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    login: Mapped[str_100]
    password: Mapped[str_100]
    when_reg: Mapped[created_at]

    balances: Mapped[list["UsersBalance"]] = relationship(
        back_populates="user",
    )

    balances_eth: Mapped[list["UsersBalance"]] = relationship(
        back_populates="user",
        primaryjoin="and_(Users.id == UsersBalance.user_id, UsersBalance.currency == 'ETH')",
        viewonly=True,
    )


class UsersBalance(Base):
    __tablename__ = "users_balance"

    id: Mapped[intpk]
    currency: Mapped[str_100 | None]
    amount: Mapped[float | None]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["Users"] = relationship(
        back_populates="balances",
    )

    used_type_of_trade: Mapped[list["TypesOfTrade"]] = relationship(
        back_populates="used_user_balance",
        secondary="types_of_balances",
        lazy="selectin",
    )


class TypesOfTrade(Base):
    __tablename__ = "types_of_trade"

    id: Mapped[intpk]
    type: Mapped[str_100]

    used_user_balance: Mapped[list["UsersBalance"]] = relationship(
        back_populates="used_type_of_trade", secondary="types_of_balances"
    )


class TypesOfBalances(Base):
    __tablename__ = "types_of_balances"

    user_balance_id: Mapped[int] = mapped_column(
        ForeignKey("users_balance.id", ondelete="CASCADE"), primary_key=True
    )
    type_of_trade_id: Mapped[int] = mapped_column(
        ForeignKey("types_of_trade.id", ondelete="CASCADE"), primary_key=True
    )
