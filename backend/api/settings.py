from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import models
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/settings", tags=["settings"])

class SettingUpdate(BaseModel):
    value: str

class SettingSchema(BaseModel):
    id: int
    key: str
    value: str
    description: str

    class Config:
        from_attributes = True

@router.get("/")
def get_settings(db: Session = Depends(get_db)):
    return db.query(models.AppSetting).all()

@router.put("/{key}")
def update_setting(key: str, update: SettingUpdate, db: Session = Depends(get_db)):
    setting = db.query(models.AppSetting).filter(models.AppSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting.value = update.value
    db.commit()
    return {"status": "success"}
