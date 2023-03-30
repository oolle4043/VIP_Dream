from fastapi import APIRouter
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc
from db import get_db

import models, schemas

router = APIRouter(prefix="/arduino",tags=["arduino"])

status_success = {"status_SUCCESS": 200}
status_false = {"status_FALSE": 401}

@router.post("/device/{user_id}/{device_code}/", status_code=200)
async def device(user_id: str, device_code: str, db: Session = Depends(get_db)):
    """
    디바이스 등록 API
    """
    user = db.query(models.User).filter_by(user_id=user_id).first()

    if not user:
        return status_false

    device = db.query(models.Device).filter_by(device_user_id=user.id).first()

    if device:
        db.query(models.Device).filter(models.Device.device_user_id == user.id).update({"device_code":device_code})
        return status_success

@router.post("/arduino/{user_id}/{temperature}/{humidity}/{air_pollution}/{fine_dust}/", status_code=200)
async def arduino(user_id: str, temperature: int, humidity: int, air_pollution: int, fine_dust: int, db: Session = Depends(get_db)):
    """
    센서 API
    """
    user = db.query(models.User).filter_by(user_id=user_id).first()
    device = db.query(models.Device).filter_by(device_user_id=user.id).first()
    arduino_sensor = db.query(models.Arduino).filter_by(arduino_user_id = user.id).first()

    if not user or not device:
        return status_false

    if not arduino_sensor:
        models.Arduino.create(db, auto_commit=True, arduino_user_id=user.id, temperature=temperature, humidity=humidity, air_pollution=air_pollution, fine_dust = fine_dust)
        return status_success
    else:
        arduino_sensor.temperature = temperature
        arduino_sensor.humidity = humidity
        arduino_sensor.air_pollution = air_pollution
        arduino_sensor.fine_dust = fine_dust
        db.add(arduino_sensor)
        db.commit()
        return status_success

@router.get("/arduino/{user_id}/{device_code}/", status_code=200)
async def alarm_status(user_id:str, device_code: str, db:Session = Depends(get_db)):
    """
    알람 On, Off API
    """
    id_exist = db.query(models.User).filter_by(user_id=user_id).first()
    alarm_info = db.query(models.Device.alarm_status).filter_by(device_user_id=id_exist.id).first()

    info = {"alarm_status":alarm_info.alarm_status, "status": 200}

    if not alarm_status:
        return status_false

    return info
