import os

from typing import List, Optional, Any
from fastapi import FastAPI, Depends, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from api.schemas import *
from api.models import Base, Dog, User
from api.database import SessionLocal, engine
from .deps import get_db, pwd_context
from .utils import *


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(DBSessionMiddleware,
                   db_url=os.environ["DATABASE_URL"])


@app.get('/')
def dog_api(db: Session=Depends(get_db)) -> Any:
    """
    root endpoint describing the api
    """
    return {
        "DogsAPI": "This is an API to create dogs with its owners go to /docs or /redoc to see the endpoints"
    }


@app.get('/api/dogs', response_model=List[DogsList])
def get_dogs(db: Session=Depends(get_db)) -> Any:
    """
    Retrieve all dogs
    """
    return db.query(Dog).all()


@app.get('/api/dogs/is_adopted', response_model=List[DogsList])
def get_adopted(db: Session=Depends(get_db)) -> Any:
    """
    Retrieve all dogs that are adopted
    """
    return db.query(Dog).filter(Dog.is_adopted).all()


@app.get('/api/dogs/{name}', response_model=DogsList)
def get_dog(name: str, db: Session=Depends(get_db)) -> Any:
    """
    Get dog by its name
    """
    dog = db.query(Dog).filter(Dog.name == name).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog does not exists")
    return dog


@app.post('/api/dogs/{name}', response_model=DogInfo)
def create_dog(
    name: str,
    owner_id: Optional[str]=None,
    db: Session=Depends(get_db)
) -> Any:
    """
    Create a new dog
    """
    db_dog = dog_creation(name, owner_id)
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
def update_dog(
    name: str,
    owner_id: Optional[str]=None,
    db: Session=Depends(get_db)
) -> Any:
    """
    Updated dog
    """
    dog = db.query(Dog).filter(Dog.name == name).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog does not exists")

    db.query(Dog).filter(Dog.name == name).update(
        dog_update_entity(owner_id),
        synchronize_session=False
    )
    db.commit()
    return db.query(Dog).filter(Dog.name == name).first()


@app.delete('/api/dogs/{name}')
def delete_dog(name: str, db: Session=Depends(get_db)) -> Any:
    """
    Delete dog
    """
    dog = db.query(Dog).filter(Dog.name == name).first()
    if not dog:
        raise HTTPException(status_code=404, detail="Dog does not exists")
    db.delete(dog)
    db.commit()

    return {
        "status": True,
        "message": "This dog has been deleted successfully"
    }


@app.get('/api/users', response_model=List[UserList])
def get_users(db: Session=Depends(get_db)) -> Any:
    """
    Retrieve all users
    """
    return db.query(User).all()


@app.post('/api/user', response_model=UserList)
def create_user(
        user: UserInput,
        db: Session=Depends(get_db)
) -> Any:
    """
    Create new user
    """
    username = db.query(User).filter(User.username == user.username).first()
    if username:
        raise HTTPException(status_code=404, detail="User already exists")
    db_user = user_creation(user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db.query(User).filter(User.id == db_user.id).first()


@app.put('/api/user/{id}', response_model=UserList)
def update_user(
        id: str,
        user: UserUpdate,
        db: Session=Depends(get_db)
) -> Any:
    """
    Update user
    """
    username = db.query(User).filter(User.id == id).first()
    if not username:
        raise HTTPException(status_code=404, detail="User does not exists")

    db.query(User).filter(User.id == id).update(
        user_update_entity(user),
        synchronize_session=False
    )
    db.commit()
    return db.query(User).filter(User.id == id).first()


@app.delete('/api/user/{id}')
def delete_user(id: str, db: Session=Depends(get_db)) -> Any:
    """
    Delete user
    """
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exists")
    db.delete(user)
    db.commit()

    return {
        "status": True,
        "message": "This user has been deleted successfully"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
