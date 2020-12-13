import requests
import uuid
from datetime import datetime as dt
from typing import List
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from models import DogsList, DogDelete, Base
from database import SessionLocal, engine


Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @app.on_event("startup")
# async def startup():
#     await database.connect()


# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()


# @app.get('/api/dogs', response_model=List[DogsList])
# async def get_dogs():
#     query = dogs.select()
#     return await database.fetch_all(query)


# @app.get('/api/dogs/is_adopted', response_model=List[DogsList])
# async def get_adopted():
#     query = dogs.select().where(dogs.c.is_adopted)
#     return await database.fetch_all(query)


# @app.get('/api/dogs/{name}', response_model=DogsList)
# async def get_dog(name: str):
#     query = dogs.select().where(dogs.c.name == name)
#     return await database.fetch_one(query)

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)
@app.post('/api/dogs/{name}', response_model=DogsList)
async def create_dog(name: str, adopted: bool):
    gID = str(uuid.uuid1())
    gDate = str(dt.now())

    # getting random image in dog ceo API
    response = requests.get('https://dog.ceo/api/breeds/image/random').json()
    dog_image_url = response['message']

    query = dogs.insert().values(
        id=gID,
        name=name,
        picture=dog_image_url,
        create_date=gDate,
        is_adopted=adopted
    )
    await database.execute(query)
    return {
        "id": gID,
        "name": name,
        "picture": dog_image_url,
        "create_date": gDate,
        "is_adopted": adopted
    }


# @app.put('/api/dogs/{name}', response_model=DogsList)
# async def update_dog(name: str, adopted: bool):
#     gDate = str(dt.now())
#     query = dogs.update().where(dogs.c.name == name).values(
#         name=name,
#         is_adopted=adopted,
#         create_date=gDate
#     )
#     await database.execute(query)

#     return await get_dog(name)


# @app.delete('/api/dogs/{name}')
# async def delete_dog(dog: DogDelete):
#     query = dogs.delete().where(dogs.c.name == dog.name)
#     print(query)
#     await database.execute(query)

#     return {
#         "status": True,
#         "message": "This dog has been deleted successfully"
#     }
