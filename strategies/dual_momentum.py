import time
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
            if df is None or len(df) < 2:
                return -999.0
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

        # Remove assets that failed to calculate
        valid_scores = {k: v for k, v in momentum_scores.items() if v != -999.0}
        
        if not valid_scores:
            logger.error("Failed to calculate momentum for all risk assets. Aborting rebalance.")
            return

        # Find asset with highest momentum
        best_asset = max(valid_scores, key=valid_scores.get)
        highest_score = valid_scores[best_asset]

        # Dual Momentum Logic:
        # 1. Relative Momentum: Pick the best among risk assets.
        # 2. Absolute Momentum: If the best is negative, go to safe asset.
        target_asset = best_asset if highest_score > 0 else self.safe_asset
        logger.info(f"Target asset for this period: {target_asset}")

        # Execute rebalance
        try:
            # 1. Close all holdings that are not the target asset
            all_assets = self.risk_assets + [self.safe_asset]
            for asset in all_assets:
                if asset != target_asset:
                    self.broker.close_all_positions(asset)
            
            # Short wait for orders to settle
            time.sleep(2)
            
            # 2. Check if we already hold the target asset
            current_qty = self.broker.get_position_qty(target_asset)
            if current_qty > 0:
                logger.info(f"Already holding {target_asset}. Rebalance complete.")
                return
                
            # 3. Get available USDT balance (using 95% to avoid margin errors)
            balance = self.broker.exchange.fetch_balance()
            free_usdt = float(balance.get('USDT', {}).get('free', 0.0))
            invest_amount = free_usdt * 0.95
            
            if invest_amount < 10.0:  # Arbitrary min limit for futures
                logger.warning(f"Insufficient available USDT ({free_usdt}) to buy {target_asset}.")
                return
                
            # 4. Buy target asset
            current_price = self.broker.get_ticker_price(target_asset)
            target_qty = invest_amount / current_price
            
            logger.info(f"REBALANCE ACTION: Switching capital to {target_asset}. Buying {target_qty} units.")
            self.broker.place_market_order(target_asset, 'buy', target_qty)
            
        except Exception as e:
            logger.error(f"Error during rebalance execution: {e}")

if __name__ == "__main__":
    assets = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    safe = "USDC/USDT"
    bot = DualMomentumBot(assets, safe)
    bot.rebalance()
