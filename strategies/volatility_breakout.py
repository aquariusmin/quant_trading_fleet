import time
import datetime
from brokers.kis_broker import KISBroker
from config.settings import config
from core.logger import get_logger

logger = get_logger("volatility_breakout")

class VolatilityBreakoutBot:
    def __init__(self, symbol: str):
        self.broker = KISBroker()
        self.symbol = symbol
        self.k = config.SHORT_TERM_K
        self.investment_amount = config.SHORT_TERM_INVESTMENT_AMOUNT
        self.target_price = None
        self.holdings = 0
        
    def calculate_target_price(self):
        """
        Calculate target price based on yesterday's range.
        Target = Today's Open + (Yesterday's High - Yesterday's Low) * K
        """
        today = datetime.datetime.now().strftime("%Y%m%d")
        # Fetch last 2 days to get yesterday's high/low
        df = self.broker.get_ohlcv(self.symbol, "20230101", today) # Large enough start date
        if len(df) < 2:
            logger.error("Not enough historical data to calculate target price.")
            return None
        
        yesterday = df.iloc[-2]
        today_open = df.iloc[-1]['open']
        
        range_val = yesterday['high'] - yesterday['low']
        self.target_price = today_open + (range_val * self.k)
        logger.info(f"Target Price for {self.symbol} calculated: {self.target_price} (K={self.k})")
        return self.target_price

    def get_max_quantity(self, price: float) -> int:
        return int(self.investment_amount // price)

    def run(self):
        """
        Main execution loop for intraday trading.
        """
        logger.info(f"Starting Volatility Breakout Bot for {self.symbol}...")
        self.calculate_target_price()
        
        while True:
            try:
                now = datetime.datetime.now()
                # Market close time (KST 15:20 for domestic stocks)
                if now.hour == 15 and now.minute >= 20:
                    if self.holdings > 0:
                        logger.info("Market closing soon. Flattening positions...")
                        self.broker.place_market_order(self.symbol, "sell", self.holdings)
                        self.holdings = 0
                    logger.info("Trading day ended. Exiting loop.")
                    break
                
                # Market not yet open
                if now.hour < 9:
                    time.sleep(60)
                    continue

                current_price = self.broker.get_ticker_price(self.symbol)
                
                # Check for breakout
                if self.holdings == 0 and current_price >= self.target_price:
                    qty = self.get_max_quantity(current_price)
                    if qty > 0:
                        logger.info(f"Breakout detected! Price: {current_price} >= Target: {self.target_price}")
                        self.broker.place_market_order(self.symbol, "buy", qty)
                        self.holdings = qty
                    else:
                        logger.warning("Investment amount too low for 1 share.")

                time.sleep(10) # Poll every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in execution loop: {e}")
                time.sleep(30)

if __name__ == "__main__":
    # Example: Trading KODEX Leverage (122630)
    bot = VolatilityBreakoutBot("122630")
    bot.run()
