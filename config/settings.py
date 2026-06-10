from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Environment Modes
    CRYPTO_MODE: Literal["testnet", "real"] = "testnet"
    STOCK_MODE: Literal["mock", "real"] = "mock"

    # Binance Credentials
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""

    # KIS Credentials
    KIS_APP_KEY: str = ""
    KIS_APP_SECRET: str = ""
    KIS_CANO: str = ""
    KIS_ACNT_PRDT_CD: str = "01"

    # Strategy Parameters
    SHORT_TERM_K: float = 0.5
    SHORT_TERM_INVESTMENT_AMOUNT: float = 100.0
    LONG_TERM_LOOKBACK_DAYS: int = 90

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

config = Settings()
