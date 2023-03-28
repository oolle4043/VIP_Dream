from fastapi import APIRouter
from requests import Session
from fastapi.params import Depends
from sqlalchemy import desc
from db import get_db

import models, schemas, datetime

router = APIRouter(prefix="/android",tags=["android"])

async def is_login_id_exist(login_id_str: str,db:Session = Depends(get_db)):
    #같은 id가 있는지 확인하는 함수
    get_login_id = db.query(models.User.user_id).filter_by(user_id=login_id_str).first()
    if get_login_id:
        return True
    else:
        return False


@router.get("/device_info/{user_id}", status_code=200)
async def main(user_id: str, db: Session = Depends(get_db)):
    """
    device info 값 송출
    """
    id_exist = db.query(models.User).filter_by(user_id=user_id).first()
    device_info = db.query(models.Device.device_name, models.Device.device_code).filter_by(device_user_id=id_exist.id).first()

    info = {"device_name": device_info.device_name, "device_code": device_info.device_code, "status": 200}

    if info == None:
        return {"result":"FALSE"}, 401
    if id_exist:
        return info
    else:
        return {"result":"FALSE"}, 401
    

@router.post("/register/{user_id}/{user_pw}/{user_name}/{user_email}/",status_code=200)
async def register(user_id: str, user_pw:str, user_name: str, user_email:str,db:Session = Depends(get_db)):
    """
    회원가입 API
    """
    id_exist = db.query(models.User.user_id).filter_by(user_id=user_id).first()
    email_exist = db.query(models.User.user_email).filter_by(user_email=user_email).first()

    if not user_id or not user_pw:
        return {"result":"FALSE"}, 401
    if id_exist:
        return {"result":"FALSE"}, 405
    if email_exist:
        return {"result":"FALSE"}, 405
    
    models.User.create(db, auto_commit=True, user_pw=user_pw, user_id=user_id, user_name=user_name, user_email=user_email)

    return {"result":"200"}

@router.get("/id_check/{user_id}",status_code=200)
async def idcheck(user_id: str,db:Session = Depends(get_db)):
    """
    아이디 중복 확인 API
    """
    is_exist = db.query(models.User.user_id).filter_by(user_id=user_id).first()
    if is_exist:
        return {"result":"FALSE"}, 405
    else:
        return {"result":"200"}, 200
    
@router.get("/email_check/{user_email}",status_code=200)
async def email_check(user_email: str,db:Session = Depends(get_db)):
    """
    이메일 중복 확인 API
    """
    email_exist = db.query(models.User.user_email).filter_by(user_email=user_email).first()
    if email_exist:
        return {"result":"FALSE"}, 401
    else:
        return {"result":"200"}, 200

@router.get("/login/{login_id}/{login_pw}/",status_code=200)
async def login(login_id: str, login_pw:str,db:Session = Depends(get_db)):
    """
    로그인 API
    """
    is_exist = await is_login_id_exist(login_id,db)
    db_user_info = db.query(models.User).filter_by(user_id=login_id).first()

    if is_exist == True:
        if db_user_info.user_pw == login_pw:
            return {"result":"True"}, 200
        else:
            return {"result":"FALSE"}, 401
    else:
        return {"result":"FALSE"}, 401
    
@router.get("/logout/{login_id}/{login_pw}/",status_code=200)
async def logout(login_id: str, login_pw:str,db:Session = Depends(get_db)):
    """
    로그아웃 API
    """
    now = datetime.datetime.now()
    
    get_user = db.query(models.User).filter_by(user_id=login_id, user_pw=login_pw).first()

    if get_user:
        get_user.updated_at = now
        db.commit()
        return {"result":"TRUE"}, 200
    else:
        return {"result":"FALSE"}, 401

@router.get("/id_find/{user_name}/{user_email}/",status_code=200)
async def id_find(user_name: str, user_email:str,db:Session = Depends(get_db)):
    """
    ID 찾기 API
    """
    is_exist_name = db.query(models.User.user_name).filter_by(user_name = user_name).first()
    is_exist_email = db.query(models.User.user_email).filter_by(user_email = user_email).first()

    if is_exist_name and is_exist_email:
        user_id = db.query(models.User.user_id).filter_by(user_name = user_name, user_email = user_email).first()
        id_send = {"user_id": user_id.user_id, "sucess": 200}
        return id_send
    else:
        return {"result":"FALSE"}, 401

@router.get("/pw_find/{user_id}/{user_name}/{user_email}/",status_code=200)
async def id_find(user_id: str, user_name: str, user_email:str,db:Session = Depends(get_db)):
    """
    PW 찾기 API
    """
    is_exist_id = db.query(models.User.user_id).filter_by(user_id = user_id).first()
    is_exist_name = db.query(models.User.user_name).filter_by(user_name = user_name).first()
    is_exist_email = db.query(models.User.user_email).filter_by(user_email = user_email).first()

    if is_exist_id and is_exist_name and is_exist_email:
        user_pw = db.query(models.User.user_pw).filter_by(user_id = user_id, user_name = user_name, user_email = user_email).first()
        pw_send = {"user_pw": user_pw.user_pw, "sucess": 200}
        return pw_send
    else:
        return {"result":"FALSE"}, 401
    
@router.get("/user_info/{user_id}/", status_code=200)
async def user_info(user_id: str, db: Session = Depends(get_db)):
    """
    user_info
    """
    info = db.query(models.User.user_id, models.User.user_name, models.User.user_email, models.User.user_pw).filter_by(user_id=user_id).first()

    info_send = {"user_id": info.user_id, "user_name": info.user_name, "user_email": info.user_email, "user_pw": info.user_pw, "status": 200}

    return info_send

@router.put("/pw_update/{user_id}/{old_user_pw}/{new_user_pw}/",status_code=200)
async def pw_update(user_id: str, old_user_pw:str, new_user_pw: str, db:Session = Depends(get_db)):
    """
    PW 수정 API
    """
    get_id = db.query(models.User.user_id).filter_by(user_id=user_id).first()
    get_pw = db.query(models.User.user_pw).filter_by(user_pw=old_user_pw).first()

    if get_id and get_pw:
        db.query(models.User).filter(models.User.user_pw == old_user_pw).update({"user_pw":new_user_pw})
        db.commit()
        return {"result":"TRUE"}, 200
    
    return {"result":"FALSE"}, 401
        
@router.post("/device/{user_id}/{device_code}/{device_name}/",status_code=200)
async def device(device_code: str, user_id: str, device_name:str, db:Session = Depends(get_db)):
    """
    device 등록 API
    """
    device_user_id = db.query(models.User.id).filter_by(user_id=user_id).scalar_subquery()
    models.Device.create(db, auto_commit=True, device_code=device_code, device_user_id = device_user_id, device_name = device_name, alarm_status = True)

    is_exist = await is_login_id_exist(user_id,db)
    if is_exist == True:
        return {"result":"200"}, 200
    else:
        return {"result":"FALSE"}, 405
    
@router.delete("/device_sensor/{user_id}/{device_code}/",status_code=200)
async def device(device_code: str, user_id: str, db:Session = Depends(get_db)):
    """
    기기 제거 API
    """
    device_user_id = db.query(models.User.id).filter_by(user_id = user_id).scalar_subquery()
    debive_exist_code = db.query(models.Device.device_code).filter_by(device_user_id = device_user_id).first()

    if debive_exist_code:
        db.query(models.Device).filter(models.Device.device_code == device_code).delete()
        db.commit()
        return {"result":"200"}, 200
    else:
        return {"result":"FALSE"}, 401
    
@router.get("/device_sensor/{user_id}/{device_code}/", status_code=200)
async def device_info(user_id: str, device_code: str, db: Session = Depends(get_db)):
    """
    센서 값 받아오는 API
    """
    device_user = db.query(models.User.id).filter_by(user_id=user_id).first()
    if not device_user:
        return {"result": "FALSE"}, 401
    device = db.query(models.Device).filter_by(device_user_id=device_user.id, device_code=device_code).first()
    if not device:
        return {"result": "FALSE"}, 401

    info = db.query(models.Arduino.temperature, models.Arduino.humidity, models.Arduino.air_pollution, models.Arduino.fine_dust).filter_by(arduino_user_id=device.id).first()
    info_send = {"temperature": info.temperature, "humidity": info.humidity, "air_pollution": info.air_pollution, "usefine_dustr_pw": info.fine_dust, "status": 200}
    return info_send

@router.delete("/user_delete/{user_id}/{user_pw}",status_code=200)
async def user_delete(user_id: str, user_pw:str, db:Session = Depends(get_db)):
    """
    계정 삭제 API
    """
    exist_user_id = db.query(models.User.user_id).filter_by(user_id = user_id).scalar_subquery()
    print(exist_user_id)
    exist_user_pw = db.query(models.User.user_pw).filter_by(user_pw = exist_user_id).first()
    print(exist_user_pw)

    if exist_user_pw:
        db.query(models.User).filter(models.User.user_pw == user_pw).delete()
        db.commit()
        return {"result":"200"}, 200
    else:
        return {"result":"FALSE"}, 401

@router.post("/alarm_status/{user_id}/{device_code}/{alarm_status}/",status_code=200)
async def alarm_status(user_id:str, device_code: str, alarm_status: str, db:Session = Depends(get_db)):
    """
    알람 On, Off API
    """
    exist_user = db.query(models.User).filter_by(user_id=user_id).first()
    if not exist_user:
            return {"result": "FALSE"}, 401

    device = db.query(models.Device).filter_by(device_code=device_code, device_user_id=exist_user.id).first()
    if not device:
        return {"result": "FALSE"}, 401

    device.alarm_status = alarm_status
    db.commit()
    return {"result": "200"}, 200
