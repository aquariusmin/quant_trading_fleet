import time
import datetime
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
        self.investment_amount = config.SHORT_TERM_INVESTMENT_AMOUNT
        self.target_price = None
        self.holdings = 0
        
        if broker_type == 'kis':
            self.broker = KISBroker()
        else:
            self.broker = BinanceBroker()
        
    def calculate_target_price(self):
        """
        Calculate target price based on yesterday's range.
        """
        if self.broker_type == 'kis':
            today = datetime.datetime.now().strftime("%Y%m%d")
            # Fetch last few days to be safe
            df = self.broker.get_ohlcv(self.symbol, "20240101", today, is_overseas=self.is_overseas)
        else:
            df = self.broker.get_ohlcv(self.symbol, timeframe='1d', limit=2)
            
        if len(df) < 2:
            logger.error(f"Not enough historical data for {self.symbol}.")
            return None
        
        yesterday = df.iloc[-2]
        today_open = df.iloc[-1]['open']
        
        range_val = yesterday['high'] - yesterday['low']
        self.target_price = today_open + (range_val * self.k)
        logger.info(f"[{self.symbol}] Target Price: {self.target_price} (K={self.k})")
        return self.target_price

    def get_max_quantity(self, price: float) -> Union[int, float]:
        if self.broker_type == 'kis':
            return int(self.investment_amount // price)
        else:
            # For crypto, we can use float amounts
            return self.investment_amount / price

    def run(self):
        logger.info(f"Starting {self.broker_type.upper()} Breakout Bot for {self.symbol}...")
        self.calculate_target_price()
        
        while True:
            try:
                now = datetime.datetime.now()
                
                # Market Hours Logic (Specific to KIS Domestic/US)
                if self.broker_type == 'kis':
                    if not self.is_overseas:
                        # Domestic: 09:00 ~ 15:20
                        if now.hour == 15 and now.minute >= 20:
                            if self.holdings > 0:
                                self.broker.place_market_order(self.symbol, "sell", self.holdings)
                                self.holdings = 0
                            logger.info("Domestic Market closed. Exiting.")
                            break
                        if now.hour < 9: 
                            time.sleep(60); continue
                    else:
                        # US Market: Very rough estimate (22:30 ~ 05:00 KST)
                        # In production, use a proper market calendar.
                        if now.hour == 5: # Close at 5 AM KST
                            if self.holdings > 0:
                                self.broker.place_market_order(self.symbol, "sell", self.holdings, is_overseas=True)
                                self.holdings = 0
                            logger.info("US Market closed. Exiting.")
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
                        self.holdings = qty

                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Loop error for {self.symbol}: {e}")
                time.sleep(30)

if __name__ == "__main__":
    import sys
    # Usage: python strategies/universal_breakout.py [kis|binance] [symbol] [is_overseas: true|false]
    b_type = sys.argv[1] if len(sys.argv) > 1 else 'kis'
    sym = sys.argv[2] if len(sys.argv) > 2 else '005930'
    overseas = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    bot = UniversalBreakoutBot(b_type, sym, overseas)
    bot.run()
