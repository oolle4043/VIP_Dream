from fastapi import APIRouter
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc
from db import get_db

import models, schemas

router = APIRouter(prefix="/arduino",tags=["arduino"])

@router.post("/device/{user_id}/{device_code}/", status_code=200)
async def device(user_id: str, device_code: str, db: Session = Depends(get_db)):
    """
    디바이스 등록 API
    """
    user = db.query(models.User).filter_by(user_id=user_id).first()

    if not user:
        return {"result": "false"}, 401

    device = db.query(models.Device).filter_by(device_user_id=user.id).first()

    if device:
        db.query(models.Device).filter(models.Device.device_user_id == user.id).update({"device_code":device_code})
        return {"result": "200"}, 200

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

@router.get("/arduino/{user_id}/{device_code}/", status_code=200)
async def alarm_status(user_id:str, device_code: str, db:Session = Depends(get_db)):
    """
    알람 On, Off API
    """
    id_exist = db.query(models.User).filter_by(user_id=user_id).first()
    alarm_info = db.query(models.Device.alarm_status).filter_by(device_user_id=id_exist.id).first()

    info = {"alarm_status":alarm_info.alarm_status, "status": 200}

    if not alarm_status:
        return {"result": "false"}, 401

    return info
    