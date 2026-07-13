from enum import Enum


class Currency(str, Enum):  # ← Наследуемся от str!
    USDT = "USDT"
    BTC = "BTC"
    ETH = "ETH"
    RUB = "RUB"
    BGB = "BGB"
    SOL = "SOL"
    ROL = "ROL"

    @property
    def full_name(self) -> str:
        names = {
            "USDT": "Tether",
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "RUB": "Ruble",
            "BGB": "Bitget Token",
            "SOL": "Solana Token",
            "ROL": "Rolana Token",
        }
        return names.get(self.value, "Unknown")

    @property
    def price_min_deposit(self) -> float:
        deposits = {
            "USDT": 1.0,
            "BTC": 0.00001,
            "ETH": 0.01,
            "RUB": 80.0,
            "BGB": 1.0,
            "SOL": 1.0,
            "ROL": 1.0,
        }
        return deposits.get(self.value, 1.0)


class AccountType(Enum):
    spot = "Spot"
    bots = "Bots"
    margin = "Margin"
    copy_trading = "Copy Trading"
    futures = "Futures"
