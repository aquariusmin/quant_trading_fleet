from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
import datetime
from backend.database.db import Base
import enum

class BotType(enum.Enum):
    KIS = "kis"
    BINANCE = "binance"

class BotState(Base):
    __tablename__ = "bot_states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g. "kospi_bot"
    symbol = Column(String)
    broker_type = Column(String) # "kis", "binance"
    is_overseas = Column(Boolean, default=False)
    is_running = Column(Boolean, default=False)
    last_run = Column(DateTime, default=datetime.datetime.utcnow)

class TradeHistory(Base):
    __tablename__ = "trade_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    bot_name = Column(String)
    symbol = Column(String)
    side = Column(String) # "buy", "sell"
    price = Column(Float)
    qty = Column(Float)
    total_amount = Column(Float)
    broker_type = Column(String)

class AppSetting(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
    description = Column(String, nullable=True)
