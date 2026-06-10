import asyncio
import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from backend.database.db import SessionLocal
from backend.models import models
from strategies.universal_breakout import UniversalBreakoutBot
from strategies.dual_momentum import DualMomentumBot
from core.logger import get_logger

logger = get_logger("bot_manager")

class BotManager:
    def __init__(self):
        self.active_bots: Dict[str, asyncio.Task] = {}
        
    async def start_bot(self, bot_name: str):
        if bot_name in self.active_bots:
            logger.warning(f"Bot {bot_name} is already running.")
            return False
        
        db = SessionLocal()
        bot_db = db.query(models.BotState).filter(models.BotState.name == bot_name).first()
        if not bot_db:
            logger.error(f"Bot {bot_name} configuration not found in database.")
            db.close()
            return False
        
        # Mark as running in DB
        bot_db.is_running = True
        db.commit()
        db.close()
        
        # Start the bot task
        task = asyncio.create_task(self._run_bot_loop(bot_name))
        self.active_bots[bot_name] = task
        logger.info(f"Bot {bot_name} started.")
        return True

    async def stop_bot(self, bot_name: str):
        if bot_name not in self.active_bots:
            logger.warning(f"Bot {bot_name} is not running.")
            return False
        
        # Cancel the task
        self.active_bots[bot_name].cancel()
        del self.active_bots[bot_name]
        
        # Update DB
        db = SessionLocal()
        bot_db = db.query(models.BotState).filter(models.BotState.name == bot_name).first()
        if bot_db:
            bot_db.is_running = False
            db.commit()
        db.close()
        
        logger.info(f"Bot {bot_name} stopped.")
        return True

    async def _run_bot_loop(self, bot_name: str):
        try:
            db = SessionLocal()
            bot_db = db.query(models.BotState).filter(models.BotState.name == bot_name).first()
            
            if bot_name == "long_term_bot":
                # Dual Momentum is a one-time rebalance
                bot = DualMomentumBot(["BTC/USDT", "ETH/USDT", "SOL/USDT"], "USDC/USDT")
                bot.rebalance()
                # Auto-stop after completion
                bot_db.is_running = False
                db.commit()
                if bot_name in self.active_bots:
                    del self.active_bots[bot_name]
            else:
                # Universal Breakout Bot
                bot = UniversalBreakoutBot(
                    bot_db.broker_type, 
                    bot_db.symbol, 
                    bot_db.is_overseas
                )
                # We'll modify run() to be an async method that respects cancellation
                await bot.run_async()
                
            db.close()
        except asyncio.CancelledError:
            logger.info(f"Bot {bot_name} loop cancelled.")
        except Exception as e:
            logger.error(f"Error in bot {bot_name} loop: {e}")
            db = SessionLocal()
            bot_db = db.query(models.BotState).filter(models.BotState.name == bot_name).first()
            if bot_db:
                bot_db.is_running = False
                db.commit()
            db.close()

bot_manager = BotManager()
