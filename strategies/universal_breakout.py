import time
import datetime
import sys
import signal
from typing import Union
from brokers.kis_broker import KISBroker
from brokers.binance_broker import BinanceBroker
from config.settings import config
from core.logger import get_logger

logger = get_logger("universal_breakout")

class UniversalBreakoutBot:
    def __init__(self, broker_type: str, symbol: str, is_overseas: bool = False):
        """
        broker_type: 'kis' or 'binance'
        symbol: e.g., '005930', 'AAPL', 'BTC/USDT'
        """
        self.broker_type = broker_type
        self.symbol = symbol
        self.is_overseas = is_overseas
        self.k = config.SHORT_TERM_K
        self.target_price = None
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)
        
        if broker_type == 'kis':
            self.broker = KISBroker()
            self.investment_amount = config.INVESTMENT_USD_STOCK if is_overseas else config.INVESTMENT_KRW
            # Sync position from broker
            self.holdings = self.broker.get_position_qty(self.symbol, is_overseas=self.is_overseas)
        else:
            self.broker = BinanceBroker()
            self.investment_amount = config.INVESTMENT_USDT_CRYPTO
            # Sync position from broker
            self.holdings = self.broker.get_position_qty(self.symbol)
            
        logger.info(f"Initialized with {self.holdings} existing holdings of {self.symbol}.")

    def handle_exit(self, signum, frame):
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.running = False

    def calculate_target_price(self):
        """
        Calculate target price based on yesterday's range.
        """
        try:
            if self.broker_type == 'kis':
                today = datetime.datetime.now().strftime("%Y%m%d")
                # Fetch last few days to be safe
                df = self.broker.get_ohlcv(self.symbol, "20240101", today, is_overseas=self.is_overseas)
            else:
                df = self.broker.get_ohlcv(self.symbol, timeframe='1d', limit=2)
                
            if df is None or len(df) < 2:
                logger.error(f"Not enough historical data for {self.symbol}.")
                return None
            
            yesterday = df.iloc[-2]
            today_open = df.iloc[-1]['open']
            
            range_val = yesterday['high'] - yesterday['low']
            self.target_price = today_open + (range_val * self.k)
            logger.info(f"[{self.symbol}] Target Price: {self.target_price} (K={self.k})")
            return self.target_price
        except Exception as e:
            logger.error(f"Error calculating target price: {e}")
            return None

    def get_max_quantity(self, price: float) -> Union[int, float]:
        if self.broker_type == 'kis':
            return int(self.investment_amount // price)
        else:
            # For crypto, we can use float amounts
            return self.investment_amount / price

    def flatten_position(self):
        if self.holdings > 0:
            logger.info(f"Flattening {self.holdings} of {self.symbol}...")
            try:
                if self.broker_type == 'kis':
                    self.broker.place_market_order(self.symbol, "sell", self.holdings, is_overseas=self.is_overseas)
                else:
                    self.broker.place_market_order(self.symbol, "sell", self.holdings)
                self.holdings = 0
            except Exception as e:
                logger.error(f"Failed to flatten position: {e}")

    async def run_async(self):
        logger.info(f"Starting {self.broker_type.upper()} Breakout Bot for {self.symbol}...")
        
        if self.calculate_target_price() is None:
            logger.error(f"Failed to calculate target price for {self.symbol}. Exiting to prevent infinite loop.")
            return
        
        while self.running:
            try:
                now = datetime.datetime.now()
                
                # Market Hours Logic (Specific to KIS Domestic/US)
                if self.broker_type == 'kis':
                    if not self.is_overseas:
                        # Domestic: 09:00 ~ 15:20
                        if now.hour >= 15 and now.minute >= 20:
                            self.flatten_position()
                            logger.info("Domestic Market closed.")
                            break
                        if now.hour < 9: 
                            await asyncio.sleep(60); continue
                    else:
                        # US Market Estimate: Close around 05:00 KST, open around 22:30 KST
                        if 5 <= now.hour < 22:
                            if self.holdings > 0:
                                self.flatten_position()
                            logger.info("US Market closed/closing.")
                            break

                current_price = self.broker.get_ticker_price(self.symbol, is_overseas=self.is_overseas) if self.broker_type == 'kis' else self.broker.get_ticker_price(self.symbol)
                
                # Breakout execution
                if self.holdings == 0 and current_price >= self.target_price:
                    qty = self.get_max_quantity(current_price)
                    if qty > 0:
                        logger.info(f"[{self.symbol}] Breakout! Price: {current_price} >= Target: {self.target_price}")
                        if self.broker_type == 'kis':
                            self.broker.place_market_order(self.symbol, "buy", qty, is_overseas=self.is_overseas)
                        else:
                            self.broker.place_market_order(self.symbol, 'buy', qty)
                        # Re-sync holdings rather than assuming success directly
                        await asyncio.sleep(2)
                        self.holdings = self.broker.get_position_qty(self.symbol, is_overseas=self.is_overseas) if self.broker_type == 'kis' else self.broker.get_position_qty(self.symbol)
                    else:
                        logger.warning(f"Investment amount too low to buy 1 unit of {self.symbol} at {current_price}.")

                await asyncio.sleep(10)
                
            except asyncio.CancelledError:
                logger.info(f"Async loop for {self.symbol} cancelled.")
                raise
            except Exception as e:
                logger.error(f"Loop error for {self.symbol}: {e}")
                await asyncio.sleep(30)
                
        # Graceful shutdown flattening
        if self.holdings > 0:
            logger.info(f"Bot stopped. Attempting to flatten positions for {self.symbol}...")
            self.flatten_position()

    def run(self):
        # Compatibility wrapper for synchronous execution
        asyncio.run(self.run_async())

if __name__ == "__main__":
    # Usage: python strategies/universal_breakout.py [kis|binance] [symbol] [is_overseas: true|false]
    b_type = sys.argv[1] if len(sys.argv) > 1 else 'kis'
    sym = sys.argv[2] if len(sys.argv) > 2 else '005930'
    overseas = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    bot = UniversalBreakoutBot(b_type, sym, overseas)
    bot.run()
