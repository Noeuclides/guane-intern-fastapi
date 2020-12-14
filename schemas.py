from pydantic import BaseModel, Field
from typing import Optional


# Models
class DogsList(BaseModel):
    id: str
    name: str
    picture: str
    create_date: str
    is_adopted: bool
    user_id: Optional[str] = None

    class Config:
        orm_mode = True


class DogInfo(BaseModel):
    id: str
    name: str
    picture: str
    create_date: str
    is_adopted: bool
    user_id: Optional[str] = None
    user_first_name: Optional[str] = None
    user_last_name: Optional[str] = None
    user_username: Optional[str] = None

    class Config:
        orm_mode = True


class UserList(BaseModel):
    id: str
    first_name: str
    last_name: str
    username: str
    email: str
    create_date: str

    class Config:
        orm_mode = True


class UserInput(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str

    class Config:
        orm_mode = True


# class DogEntry(BaseModel):
#     name: str = Field(..., example="Lazy")
#     is_adopted: bool = Field(..., example=True)


# class DogUpdate(BaseModel):
#     name: str = Field(..., example="Enter_your_dog_name")
#     is_adopted: bool = Field(..., example=True)

class DogDelete(BaseModel):
    name: str
