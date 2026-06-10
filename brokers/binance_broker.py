import ccxt
import pandas as pd
from config.settings import config
from core.logger import get_logger
from backend.database.db import SessionLocal
from backend.models import models

logger = get_logger("binance_broker")

class BinanceBroker:
    def __init__(self):
        self.mode = config.CRYPTO_MODE
        self.exchange = ccxt.binance({
            'apiKey': config.BINANCE_API_KEY,
            'secret': config.BINANCE_SECRET_KEY,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'  # Typically volatility breakout is traded on futures
            }
        })
        
        if self.mode == "testnet":
            self.exchange.set_sandbox_mode(True)
            logger.info("Binance Broker initialized in TESTNET mode.")
        else:
            logger.warning("Binance Broker initialized in REAL mode. Real money will be used.")
            
        self.exchange.load_markets()

    def get_ohlcv(self, symbol: str, timeframe: str = '1d', limit: int = 100) -> pd.DataFrame:
        """
        Fetch OHLCV data and return as a Pandas DataFrame.
        """
        try:
            bars = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise

    def get_ticker_price(self, symbol: str) -> float:
        """
        Get the current price of a symbol.
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise

    def get_position_qty(self, symbol: str) -> float:
        """
        Get the current position quantity for a symbol.
        """
        try:
            positions = self.exchange.fetch_positions(symbols=[symbol])
            for pos in positions:
                if pos['symbol'] == symbol:
                    return float(pos['info']['positionAmt'])
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching position for {symbol}: {e}")
            return 0.0

    def place_market_order(self, symbol: str, side: str, amount: float):
        """
        Place a market order.
        side: 'buy' or 'sell'
        """
        try:
            market = self.exchange.market(symbol)
            
            # Format amount to required precision
            precision_amount = float(self.exchange.amount_to_precision(symbol, amount))
            
            # Check min amount
            if 'limits' in market and 'amount' in market['limits']:
                min_amount = market['limits']['amount']['min']
                if precision_amount < min_amount:
                    logger.warning(f"Order amount {precision_amount} for {symbol} is below minimum {min_amount}.")
                    return None
                    
            logger.info(f"Placing {side} market order for {precision_amount} {symbol}...")
            order = self.exchange.create_market_order(symbol, side, precision_amount)
            
            # Log trade to DB
            try:
                price = order.get('price') or self.get_ticker_price(symbol)
                db = SessionLocal()
                new_trade = models.TradeHistory(
                    bot_name="binance_bot",
                    symbol=symbol,
                    side=side,
                    price=price,
                    qty=precision_amount,
                    total_amount=price * precision_amount,
                    broker_type="binance"
                )
                db.add(new_trade)
                db.commit()
                db.close()
            except Exception as log_e:
                logger.error(f"Failed to log trade to DB: {log_e}")

            logger.info(f"Order successful: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error placing {side} order for {symbol}: {e}")
            raise

    def close_all_positions(self, symbol: str):
        """
        Close all active positions for a given symbol.
        """
        try:
            qty = self.get_position_qty(symbol)
            if qty > 0:
                self.place_market_order(symbol, 'sell', qty)
            elif qty < 0:
                self.place_market_order(symbol, 'buy', abs(qty))
            logger.info(f"All positions for {symbol} closed.")
        except Exception as e:
            logger.error(f"Error closing positions for {symbol}: {e}")
            raise
