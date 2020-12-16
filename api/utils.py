import uuid
import requests
from datetime import datetime as dt
from typing import Dict, Optional

from api.models import Dog, User
from api.schemas import UserInput, UserUpdate


def dog_creation(name: str, owner_id: Optional[str]=None) -> Dog:
    """
    Method to create a dog instance
    """
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

    return db_dog


def dog_user_entity(user: User) -> Dict:
    """
    method to obtain a dictionary with the info of the dogs owner
    """
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

    return user_info


def dog_update_entity(owner_id: Optional[str]=None) -> Dict:
    """
    method to obtain a dictionary with the dog to update
    """
    gDate = str(dt.now())
    if owner_id:
        adopted = True
    else:
        adopted = False
        
    return {
        Dog.is_adopted: adopted,
        Dog.create_date: gDate,
        Dog.user_id: owner_id
    }
        

def user_creation(user: UserInput) -> User:
    """
    Method to create a user instance
    """
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

    return db_user


def user_update_entity(user: UserUpdate) -> Dict:
    """
    method to obtain a dictionary with the user to update
    """
    gDate = str(dt.now())
        
    return {
        User.first_name: user.first_name,
        User.last_name: user.last_name,
        User.email: user.email,
        User.create_date: gDate,
    }
