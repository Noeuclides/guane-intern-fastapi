import os
import requests
import uuid
from datetime import datetime as dt
from typing import List, Optional
from fastapi import FastAPI, Depends
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from schemas import *
from models import Base, Dog, User
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
app.add_middleware(DBSessionMiddleware,
                   db_url=os.environ["DATABASE_URL"])

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
def dog_api(db: Session=Depends(get_db)):
    return {
        "Dogs Api": "This is an API to create dogs with its owners go to /docs or /redoc to see the endpoints"
    }


@app.get('/api/dogs', response_model=List[DogsList])
def get_dogs(db: Session=Depends(get_db)):
    return db.query(Dog).all()


@app.get('/api/dogs/is_adopted', response_model=List[DogsList])
async def get_adopted(db: Session=Depends(get_db)):
    return db.query(Dog).filter(Dog.is_adopted).all()


@app.get('/api/dogs/{name}', response_model=DogsList)
async def get_dog(name: str, db: Session=Depends(get_db)):
    return db.query(Dog).filter(Dog.name == name).first()


@app.post('/api/dogs/{name}', response_model=DogInfo)
async def create_dog(
    name: str,
    owner_id: Optional[str]=None,
    db: Session=Depends(get_db)
):
    gID = str(uuid.uuid1())
    gDate = str(dt.now())
    if not owner_id:
        adopted = False
    else:
        adopted = True
    # getting random image in dog ceo API
    response = requests.get('https://dog.ceo/api/breeds/image/random').json()
    dog_image_url = response['message']
    db_dog = Dog(
        id=gID,
        name=name,
        picture=dog_image_url,
        create_date=gDate,
        is_adopted=adopted,
        user_id=owner_id
    )
    db.add(db_dog)
    db.commit()
    db.refresh(db_dog)
    user = db.query(User).filter(User.id == owner_id).first()
    if user:
        user_info = {
            "user_id": user.id,
            "user_first_name": user.first_name,
            "user_last_name": user.last_name,
            "user_username": user.username
        }
    else:
        user_info = {
            "user_id": None,
            "user_first_name": None,
            "user_last_name": None,
            "user_username": None
        }
    dog_info = {
        "id": db_dog.id,
        "name": db_dog.name,
        "picture": db_dog.picture,
        "create_date": db_dog.create_date,
        "is_adopted": db_dog.is_adopted,
    }
    dog_info.update(user_info)

    return dog_info


@app.put('/api/dogs/{name}', response_model=DogsList)
async def update_dog(
    name: str,
    owner_id: Optional[str]=None,
    db: Session=Depends(get_db)
):
    gDate = str(dt.now())
    if owner_id:
        adopted = True
    else:
        adopted = False

    db.query(Dog).filter(Dog.name == name).update(
        {
            Dog.is_adopted: adopted,
            Dog.create_date: gDate,
            Dog.user_id: owner_id
        }, synchronize_session=False
    )
    db.commit()
    return db.query(Dog).filter(Dog.name == name).first()


@app.delete('/api/dogs/{name}')
def delete_dog(name: str, db: Session=Depends(get_db)):
    dog = db.query(Dog).filter(Dog.name == name).first()
    db.delete(dog)
    db.commit()

    return {
        "status": True,
        "message": "This dog has been deleted successfully"
    }


@app.get('/api/users', response_model=List[UserList])
def get_users(db: Session=Depends(get_db)):
    return db.query(User).all()


@app.post('/api/user/{name}', response_model=UserList)
def create_user(user: UserInput, db: Session=Depends(get_db)):
    gID = str(uuid.uuid1())
    gDate = str(dt.now())

    db_user = User(
        id=gID,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        create_date=gDate,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db.query(User).filter(User.id == gID).first()


@app.put('/api/user/{id}', response_model=UserList)
def update_user(id: str, user: UserUpdate, db: Session=Depends(get_db)):
    gDate = str(dt.now())

    db.query(User).filter(User.id == id).update(
        {
            User.first_name: user.first_name,
            User.last_name: user.last_name,
            User.email: user.email,
            User.create_date: gDate,
        }, synchronize_session=False
    )
    db.commit()
    return db.query(User).filter(User.id == id).first()


@app.delete('/api/user/{id}')
def delete_user(id: str, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    db.delete(user)
    db.commit()

    return {
        "status": True,
        "message": "This user has been deleted successfully"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
