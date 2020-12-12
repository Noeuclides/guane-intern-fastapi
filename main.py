import requests
import uuid
from datetime import datetime as dt
from datetime import timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import DogsList, DogDelete
from db import database, dogs
from pydantic import BaseModel

SECRET_KEY = "7f0fa8c820e49e4e6ca606db3d6773ef5cc33e35eeb8e760c1e8f18bff740ff9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = dt.utcnow() + expires_delta
    else:
        expire = dt.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get('/api/dogs', response_model=List[DogsList])
async def get_dogs():
    query = dogs.select()
    return await database.fetch_all(query)


@app.get('/api/dogs/is_adopted', response_model=List[DogsList])
async def get_adopted():
    query = dogs.select().where(dogs.c.is_adopted)
    return await database.fetch_all(query)


@app.get('/api/dogs/{name}', response_model=DogsList)
async def get_dog(name: str):
    query = dogs.select().where(dogs.c.name == name)
    return await database.fetch_one(query)


@app.post('/api/dogs/{name}', response_model=DogsList)
async def create_dog(name: str, adopted: bool, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    print(type(user))
    print(user.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
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
        "is_adopted": adopted,
        "access_token": access_token
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

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user