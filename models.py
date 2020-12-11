from pydantic import BaseModel, Field


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
