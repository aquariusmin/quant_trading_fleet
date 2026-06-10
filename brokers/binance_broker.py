import ccxt
import pandas as pd
from config.settings import config
from core.logger import get_logger

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

    def place_market_order(self, symbol: str, side: str, amount: float):
        """
        Place a market order.
        side: 'buy' or 'sell'
        """
        try:
            logger.info(f"Placing {side} market order for {amount} {symbol}...")
            order = self.exchange.create_market_order(symbol, side, amount)
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
            positions = self.exchange.fetch_positions(symbols=[symbol])
            for pos in positions:
                amt = float(pos['info']['positionAmt'])
                if amt > 0:
                    self.place_market_order(symbol, 'sell', amt)
                elif amt < 0:
                    self.place_market_order(symbol, 'buy', abs(amt))
            logger.info(f"All positions for {symbol} closed.")
        except Exception as e:
            logger.error(f"Error closing positions for {symbol}: {e}")
            raise
