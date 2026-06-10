from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import models
from backend.api.bot_manager import bot_manager
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/bots", tags=["bots"])

class BotStatus(BaseModel):
    id: int
    name: str
    symbol: str
    broker_type: str
    is_overseas: bool
    is_running: bool

@router.get("/", response_model=List[BotStatus])
def get_bots(db: Session = Depends(get_db)):
    return db.query(models.BotState).all()

@router.post("/{bot_name}/start")
async def start_bot(bot_name: str):
    success = await bot_manager.start_bot(bot_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to start bot {bot_name}")
    return {"status": "started"}

@router.post("/{bot_name}/stop")
async def stop_bot(bot_name: str):
    success = await bot_manager.stop_bot(bot_name)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to stop bot {bot_name}")
    return {"status": "stopped"}
