import uvicorn
import datetime
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from requests import Session
from fastapi.params import Depends

import models, schemas

from db import enigne, get_db
models.Base.metadata.create_all(bind=enigne)

app = FastAPI()

@app.get("/")
def main():
    return RedirectResponse(url="/docs")

async def is_login_id_exist(login_id_str: str,db:Session = Depends(get_db)):
    #같은 id가 있는지 확인하는 함수
    get_login_id = db.query(models.User.user_id).filter_by(user_id=login_id_str).first()
    if get_login_id:
        return True
    else:
        return False

#회원가입
@app.post("/register/{user_id}/{user_pw}/{user_name}/{user_email}/",status_code=200)
async def register(user_id: str, user_pw:str, user_name: str, user_email:str,db:Session = Depends(get_db)):
    """
    회원가입 API
    """
    id_exist = db.query(models.User.user_id).filter_by(user_id=user_id).first()
    name_exist = db.query(models.User.user_name).filter_by(user_name=user_name).first()
    email_exist = db.query(models.User.user_email).filter_by(user_email=user_email).first()

    print(user_id, user_pw, user_name, user_email)

    if not user_id or not user_pw:
        return {"result":"FALSE"}, 400
    if id_exist:
        return {"result":"FALSE"}, 405
    if email_exist:
        return {"result":"FALSE"}, 405
    
    print("123123")
    
    models.User.create(db, auto_commit=True, user_pw=user_pw, user_id=user_id, user_name=user_name, user_email=user_email)

    return {"result":"200"}

@app.get("/idcheck/{user_id}",status_code=200)
async def idcheck(user_id: str,db:Session = Depends(get_db)):
    """
    아이디 중복 확인 API
    """
    is_exist = db.query(models.User.user_id).filter_by(user_id=user_id).first()
    if is_exist:
        return {"result":"FALSE"}, 405
    else:
        return {"result":"200"}

@app.get("/login/{login_id}/{login_pw}/",status_code=200)
async def login(login_id: str, login_pw:str,db:Session = Depends(get_db)):
    """
    로그인 API
    """
    is_exist = await is_login_id_exist(login_id,db)
    db_user_info = db.query(models.User).filter_by(user_id=login_id).first()
    get_id = db.query(models.User.id).filter_by(user_id=login_id).scalar_subquery()

    device_info = db.query(models.Device.device_name, models.Device.device_code).filter_by(device_user_id = get_id).all()
    print(device_info)

    if is_exist == True:
        if db_user_info.user_pw == login_pw:
            return device_info
    else:
        return {"result":"FALSE"},400
    
@app.get("/logout/{login_id}/{login_pw}/",status_code=200)
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


@app.get("/id_find/{user_name}/{user_email}/",status_code=200)
async def id_find(user_name: str, user_email:str,db:Session = Depends(get_db)):
    """
    ID 찾기 API
    """
    is_exist_name = db.query(models.User.user_name).filter_by(user_name = user_name).first()
    is_exist_email = db.query(models.User.user_email).filter_by(user_email = user_email).first()

    if is_exist_name and is_exist_email:
        user_id = db.query(models.User.user_id).filter_by(user_name = user_name, user_email = user_email).all()
        return user_id
    else:
        return {"result":"FALSE"}, 401

@app.get("/pw_find/{user_id}/{user_name}/{user_email}/",status_code=200)
async def id_find(user_id: str, user_name: str, user_email:str,db:Session = Depends(get_db)):
    """
    PW 찾기 API
    """
    is_exist_id = db.query(models.User.user_id).filter_by(user_id = user_id).first()
    is_exist_name = db.query(models.User.user_name).filter_by(user_name = user_name).first()
    is_exist_email = db.query(models.User.user_email).filter_by(user_email = user_email).first()

    if is_exist_id and is_exist_name and is_exist_email:
        user_pw = db.query(models.User.user_pw).filter_by(user_id = user_id, user_name = user_name, user_email = user_email).all()
        return user_pw
    else:
        return {"result":"FALSE"}, 401
    

@app.get("/user_info/{user_id}/",status_code=200)
async def user_info(user_id: str,db:Session = Depends(get_db)):
    """
    user_info
    """
    get_id = db.query(models.User.user_id).filter_by(user_id=user_id).first()
    get_name = db.query(models.User.user_name).filter_by(user_id=user_id).first()
    get_email = db.query(models.User.user_email).filter_by(user_id=user_id).first()
    get_pw = db.query(models.User.user_pw).filter_by(user_id=user_id).first()

    return {"user_id":get_id, "user_name":get_name, "user_email":get_email, "user_pw":get_pw}

@app.put("/pw_update/{user_id}/{old_user_pw}/{new_user_pw}/",status_code=200)
async def pw_update(user_id: str, old_user_pw:str, new_user_pw: str, db:Session = Depends(get_db)):
    """
    PW 수정 API
    """
    get_id = db.query(models.User.user_id).filter_by(user_id=user_id).first()
    get_pw = db.query(models.User.user_pw).filter_by(user_pw=old_user_pw).first()

    if get_id and get_pw:
        db.query(models.User).filter(models.User.user_pw == old_user_pw).update({"user_pw":new_user_pw})
        db.commit()
        return {"result":"TRUE"}
    
    return {"result":"FALSE"}, 401

@app.post("/arduino/{user_id}/{temperature}/{humidity}/{air_pollution}/",status_code=200)
async def arduino(user_id: str, temperature: int, humidity: int, air_pollution: int,db:Session = Depends(get_db)):
    """
    센서 API
    """
    users_id = db.query(models.User.id).filter_by(user_id=user_id).scalar_subquery()
    models.Arduino.create(db, auto_commit=True, temperature=temperature, humidity=humidity, air_pollution=air_pollution)

    if temperature and humidity and air_pollution:
        return {"result":"200"}
    
@app.get("/arduino/{user_id}/",status_code=200)
async def arduino(login_id: str, db:Session = Depends(get_db)):
    """
    센서 값 송출 API
    """
    get_id = db.query(models.User.id).filter_by(user_id=login_id).first()
    
    print(get_id)

@app.post("/device/{user_id}/{device_code}/{device_name}",status_code=200)
async def device(device_code: str, user_id: str, device_name:str, db:Session = Depends(get_db)):
    """
    device 등록 API
    """
    device_user_id = db.query(models.User.id).filter_by(user_id=user_id).scalar_subquery()
    models.Device.create(db, auto_commit=True, device_code=device_code, device_user_id = device_user_id, device_name = device_name)

    is_exist = await is_login_id_exist(user_id,db)
    if is_exist == True:
        return {"result":"200"}
    else:
        return {"result":"FALSE"}, 405



if __name__  == '__main__':
    uvicorn.run(app="main:app", 
                host="203.250.133.156",
                port=8000,
                reload=True)