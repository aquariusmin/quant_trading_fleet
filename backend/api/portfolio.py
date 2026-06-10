from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import models
from brokers.kis_broker import KISBroker
from brokers.binance_broker import BinanceBroker
from config.settings import config

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/")
def get_portfolio_summary(db: Session = Depends(get_db)):
    """
    Get a summary of all balances and holdings.
    """
    kis = KISBroker()
    binance = BinanceBroker()
    
    # KIS Domestic Holdings
    # We can extend the brokers to return full balance info
    # For now, let's return a basic structure
    
    return {
        "kis_broker": {
            "mode": config.STOCK_MODE,
            # Placeholder for actual balance fetching
            "balance_krw": "Querying..." 
        },
        "binance_broker": {
            "mode": config.CRYPTO_MODE,
            "balance_usdt": "Querying..."
        }
    }

@router.get("/trades")
def get_trade_history(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.TradeHistory).order_by(models.TradeHistory.timestamp.desc()).limit(limit).all()
