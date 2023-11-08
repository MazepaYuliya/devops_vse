"""Сервис для ветеринарной клиники"""
import datetime
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi_sqlalchemy import DBSessionMiddleware, db
from dotenv import load_dotenv
from models import Dog, DogType, Timestamp
from schema import DogSchema, TimestampSchema


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


@app.get("/", summary='Root')
def root():
    """Текстовое описание сервиса"""
    description = """
        Welcome to Dogs Veterinary Service!

        Use one of endpoints:
        - /post (POST) - return current timestamp
        - /dog (GET) - get list of dogs
        - /dog (POST) - create new dog
        - /dog/{pk} (GET) - get dog by pk
        - /dog/{pk} (POST) - update dog by pk
    """
    return PlainTextResponse(content=description)


@app.post("/post", response_model=TimestampSchema, summary='Get Post')
def post_timestamp():
    """Фиксация времени запроса"""
    new_timestamp = Timestamp(timestamp=datetime.datetime.now())
    db.session.add(new_timestamp)
    db.session.commit()
    return {
        'id': new_timestamp.id,
        'timestamp': int(round(new_timestamp.timestamp.timestamp()))
    }


@app.get("/dog", summary='Get Dogs')
def get_dogs(kind: DogType):
    """Получение списка собак по породе"""
    dogs = db.session.query(Dog).filter(Dog.kind == kind).all()
    return dogs


@app.post("/dog", response_model=DogSchema, summary='Create Dog')
def create_dog(dog: DogSchema):
    """Метод для добавления новой собаки"""
    existing_dog = db.session.query(Dog).filter(Dog.pk == dog.pk).first()
    if existing_dog:
        raise HTTPException(status_code=409, detail='PK already exists')
    db_dog = Dog(**dog.dict())
    db.session.add(db_dog)
    db.session.commit()
    return db_dog


@app.get("/dog/{pk}", response_model=DogSchema, summary='Get Dog By Pk')
def get_dog(pk: int):
    """Метод для получения информации о собаке по pk"""
    dog = db.session.query(Dog).filter(Dog.pk == pk).first()
    if not dog:
        raise HTTPException(status_code=422, detail="Item not found")
    return dog


@app.patch("/dog/{pk}", response_model=DogSchema, summary='Update Dog')
def update_dog(pk: int, dog: DogSchema):
    """Метод для обновления информации о собаке по pk"""
    db_dog = db.session.query(Dog).filter(Dog.pk == pk).first()
    if not db_dog:
        raise HTTPException(status_code=409, detail='PK is not exists')
    if pk != dog.pk:
        existing_dog = db.session.query(Dog).filter(Dog.pk == dog.pk).first()
        if existing_dog:
            raise HTTPException(
                status_code=409, detail='New PK already exists'
            )
    for key, value in vars(dog).items():
        setattr(db_dog, key, value)
    db.session.commit()
    db.session.refresh(db_dog)
    return db_dog


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
