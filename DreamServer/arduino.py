from fastapi import APIRouter
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc
from db import get_db

import models, schemas

router = APIRouter(prefix="/arduino",tags=["arduino"])

@router.post("/arduino/{user_id}/{temperature}/{humidity}/{air_pollution}/{fine_dust}/", status_code=200)
async def arduino(user_id: str, temperature: int, humidity: int, air_pollution: int, fine_dust: int, db: Session = Depends(get_db)):
    """
    센서 API
    """
    user = db.query(models.User).filter_by(user_id=user_id).first()
    if not user:
        return {"result": "false"}, 401

    device = db.query(models.Device).filter_by(device_user_id=user.id).first()
    if not device:
        return {"result": "false"}, 401

    models.Arduino.create(db, auto_commit=True, arduino_user_id=device.id, temperature=temperature, humidity=humidity, air_pollution=air_pollution, fine_dust = fine_dust)
    return {"result": "200"}, 200