import os
import urllib
import requests
import databases
import sqlalchemy
import uuid
from datetime import datetime as dt
from typing import Optional, List
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# configure database
host_server = os.environ.get('host_server', 'localhost')
db_server_port = urllib.parse.quote_plus(
    str(os.environ.get('db_server_port', '5432')))
database_name = os.environ.get('database_name', 'guanedb1')
db_username = urllib.parse.quote_plus(
    str(os.environ.get('db_username', 'postgres')))
print(db_username)
db_password = urllib.parse.quote_plus(
    str(os.environ.get('db_password', 'secret')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode', 'prefer')))
DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(
    db_username,
    db_password,
    host_server,
    db_server_port,
    database_name,
    ssl_mode
)
print(DATABASE_URL)

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

dogs = sqlalchemy.Table(
    "dogs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, unique=True),
    sqlalchemy.Column("picture", sqlalchemy.String),
    sqlalchemy.Column("create_date", sqlalchemy.String),
    sqlalchemy.Column("is_adopted", sqlalchemy.Boolean),
)



engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

# Models
class DogsList(BaseModel):
    id: str
    name: str
    picture: str
    create_date: str
    is_adopted: bool


# class DogEntry(BaseModel):
#     name: str = Field(..., example="Lazy")
#     is_adopted: bool = Field(..., example=True)


# class DogUpdate(BaseModel):
#     name: str = Field(..., example="Enter_your_dog_name")
#     is_adopted: bool = Field(..., example=True)

class DogDelete(BaseModel):
    name: str

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/api/dogs', response_model=List[DogsList])
async def get_dogs():
    query = dogs.select()
    return await database.fetch_all(query)

@app.get('/api/dogs/is_adopted', response_model=List[DogsList])
async def get_adopted():
    query = dogs.select().where(dogs.c.is_adopted == True)
    return await database.fetch_all(query)

@app.get('/api/dogs/{name}', response_model=DogsList)
async def get_dog(name: str):
    query = dogs.select().where(dogs.c.name == name)
    return await database.fetch_one(query)

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

@app.put('/api/dogs/{name}', response_model=DogsList)
async def update_dog(name: str, adopted: bool):
    gDate = str(dt.now())
    query = dogs.update().where(dogs.c.name == name).values(
        name=name,
        is_adopted=adopted,
        create_date=gDate
    )
    await database.execute(query)

    return await get_dog(name)

@app.delete('/api/dogs/{name}')
async def delete_dog(dog: DogDelete):
    query = dogs.delete().where(dogs.c.name == dog.name)
    print(query)
    await database.execute(query)

    return {
        "status": True,
        "message": "This dog has been deleted successfully"
    }