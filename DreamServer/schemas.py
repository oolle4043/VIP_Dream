from xmlrpc.client import DateTime
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    user_id: str
    user_pw: str
    user_name: str
    user_email: str

    class Config:
        orm_mode = True

class login(BaseModel):
    login_id: str
    login_pw: str

    class Config:
        orm_mode = True

class arduino(BaseModel):
    arduino_user_id: int
    temperature: int
    humidity: int
    air_pollution: int
    
    class Config:
        orm_mode = True


class device(BaseModel):
    udevice_user_id: int
    device_code: str
    device_name: str

    class Config:
        orm_mode = True
