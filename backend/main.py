from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database.db import engine, Base, get_db, SessionLocal
from backend.models import models
from backend.api import portfolio, bots, settings
from config.settings import config as app_config
import uvicorn
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quant Trading Fleet API")

app.include_router(portfolio.router, prefix="/api")
app.include_router(bots.router, prefix="/api")
app.include_router(settings.router, prefix="/api")

# Serve Frontend
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        return FileResponse("frontend/dist/index.html")

@app.on_event("startup")
def startup_event():
    # Seed initial bot configurations if not present
    db = SessionLocal()
    initial_bots = [
        {"name": "kospi_bot", "symbol": "005930", "broker_type": "kis", "is_overseas": False},
        {"name": "us_stock_bot", "symbol": "AAPL", "broker_type": "kis", "is_overseas": True},
        {"name": "crypto_breakout_bot", "symbol": "BTC/USDT", "broker_type": "binance", "is_overseas": False},
        {"name": "long_term_bot", "symbol": "PORTFOLIO", "broker_type": "binance", "is_overseas": False},
    ]
    for bot_data in initial_bots:
        exists = db.query(models.BotState).filter(models.BotState.name == bot_data["name"]).first()
        if not exists:
            new_bot = models.BotState(**bot_data)
            db.add(new_bot)
            
    # Seed initial settings
    initial_settings = [
        {"key": "SHORT_TERM_K", "value": str(app_config.SHORT_TERM_K), "description": "K-value for volatility breakout strategy"},
        {"key": "INVESTMENT_KRW", "value": str(app_config.INVESTMENT_KRW), "description": "Investment amount for domestic stocks (KRW)"},
        {"key": "INVESTMENT_USD_STOCK", "value": str(app_config.INVESTMENT_USD_STOCK), "description": "Investment amount for overseas stocks (USD)"},
        {"key": "INVESTMENT_USDT_CRYPTO", "value": str(app_config.INVESTMENT_USDT_CRYPTO), "description": "Investment amount for crypto (USDT)"},
    ]
    for s_data in initial_settings:
        exists = db.query(models.AppSetting).filter(models.AppSetting.key == s_data["key"]).first()
        if not exists:
            new_setting = models.AppSetting(**s_data)
            db.add(new_setting)
            
    db.commit()
    db.close()

@app.get("/")
def read_root():
    return {"message": "Quant Trading Fleet API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
