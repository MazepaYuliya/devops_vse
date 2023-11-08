from sqlalchemy import Enum
from enum import Enum as pyenum
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import TIMESTAMP


Base = declarative_base()


class DogType(str, pyenum):
    """Предопределенные значения пород собак"""
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"


class Dog(Base):
    """Класс для собак"""
    __tablename__ = 'dog'
    name = Column(String)
    pk = Column(Integer, primary_key=True)
    kind = Column(Enum(DogType))


class Timestamp(Base):
    """Класс для фиксации времени запросов"""
    __tablename__ = 'time_stamp'
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP(timezone=False), nullable=False)
