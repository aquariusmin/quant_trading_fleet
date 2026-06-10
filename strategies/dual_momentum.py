import datetime
import pandas as pd
from typing import List
from brokers.binance_broker import BinanceBroker
from config.settings import config
from core.logger import get_logger

logger = get_logger("dual_momentum")

class DualMomentumBot:
    def __init__(self, risk_assets: List[str], safe_asset: str):
        self.broker = BinanceBroker()
        self.risk_assets = risk_assets  # e.g., ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        self.safe_asset = safe_asset    # e.g., 'USDC/USDT' (or cash)
        self.lookback_days = config.LONG_TERM_LOOKBACK_DAYS

    def calculate_momentum(self, symbol: str) -> float:
        """
        Calculate momentum (return over lookback period).
        """
        try:
            df = self.broker.get_ohlcv(symbol, timeframe='1d', limit=self.lookback_days + 1)
            start_price = df.iloc[0]['close']
            end_price = df.iloc[-1]['close']
            momentum = (end_price - start_price) / start_price
            return momentum
        except Exception as e:
            logger.error(f"Failed to calculate momentum for {symbol}: {e}")
            return -999.0

    def rebalance(self):
        """
        Monthly rebalancing logic.
        """
        logger.info("Starting Dual Momentum Rebalancing...")
        
        momentum_scores = {}
        for symbol in self.risk_assets:
            score = self.calculate_momentum(symbol)
            momentum_scores[symbol] = score
            logger.info(f"Momentum for {symbol}: {score:.4f}")

        # Find asset with highest momentum
        best_asset = max(momentum_scores, key=momentum_scores.get)
        highest_score = momentum_scores[best_asset]

        # Dual Momentum Logic:
        # 1. Relative Momentum: Pick the best among risk assets.
        # 2. Absolute Momentum: If the best is negative, go to safe asset.
        
        target_asset = best_asset if highest_score > 0 else self.safe_asset
        logger.info(f"Target asset for this period: {target_asset}")

        # Logic for execution:
        # In a real production bot, you would:
        # 1. Fetch current balance.
        # 2. Sell current holdings that are not target_asset.
        # 3. Buy target_asset with available capital.
        
        # NOTE: For brevity, this bot logs the decision. 
        # Integration with self.broker.place_market_order would happen here.
        logger.info(f"REBALANCE ACTION: Switch all capital to {target_asset}")

if __name__ == "__main__":
    assets = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    safe = "USDC/USDT"
    bot = DualMomentumBot(assets, safe)
    bot.rebalance()
