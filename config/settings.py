from typing import Literal, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import Session
import os

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

    # Strategy Parameters (Default values)
    SHORT_TERM_K: float = 0.5
    INVESTMENT_KRW: float = 1000000.0
    INVESTMENT_USD_STOCK: float = 1000.0
    INVESTMENT_USDT_CRYPTO: float = 1000.0
    LONG_TERM_LOOKBACK_DAYS: int = 90

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_dynamic_setting(self, db: Session, key: str, default: Any):
        """
        Fetch a setting from the database, falling back to the provided default.
        """
        from backend.models.models import AppSetting
        db_setting = db.query(AppSetting).filter(AppSetting.key == key).first()
        if db_setting:
            try:
                # Basic type conversion based on default's type
                if isinstance(default, float):
                    return float(db_setting.value)
                if isinstance(default, int):
                    return int(db_setting.value)
                if isinstance(default, bool):
                    return db_setting.value.lower() == "true"
                return db_setting.value
            except:
                return default
        return default

config = Settings()
