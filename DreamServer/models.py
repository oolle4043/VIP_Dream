from enum import unique
from operator import index
from pymysql import Timestamp
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, func, DateTime, Enum
from sqlalchemy.orm import relationship
from db import Base
from sqlalchemy.orm import Session

class BaseMixin:
    id = Column(Integer, primary_key=True, index=True, unique=True)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

    def __init__(self):
        self._q = None
        self._session = None
        self.served = None

    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def create(cls, db: Session, auto_commit=False, **kwargs):
        """
        테이블 데이터 적재 전용 함수
        :param session:
        :param auto_commit: 자동 커밋 여부
        :param kwargs: 적재 할 데이터
        :return:
        """
        obj = cls()
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwargs:
                setattr(obj, col_name, kwargs.get(col_name))
        db.add(obj)
        db.flush()
        if auto_commit:
            db.commit()
        return obj

class User(Base, BaseMixin):
    __tablename__ = 'users'
    user_id = Column(String(length=255), unique = True)
    user_pw = Column(String(length=255))
    user_name = Column(String(length=255))
    user_email = Column(String(length=255), unique = True)

    device = relationship(
        "Device",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

class Device(Base, BaseMixin):
    __tablename__ = 'device'
    device_user_id = Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
    device_code = Column(String(length=255), unique = True)
    device_name = Column(String(length=255))
    alarm_status = Column(Boolean, nullable=False, default=True)

    arduino = relationship(
        "Arduino",
        back_populates="device",
        cascade="all, delete",
        passive_deletes=True,
    )

    user = relationship("User",back_populates="device")

class Arduino(Base, BaseMixin):
    __tablename__ = 'arduino'
    arduino_user_id = Column(Integer,ForeignKey("device.id",ondelete="CASCADE"))
    temperature = Column(Integer, nullable=False)
    humidity = Column(Integer, nullable=False)
    air_pollution = Column(Integer, nullable=False)
    fine_dust = Column(Integer, nullable=False)

    device = relationship("Device",back_populates="arduino")