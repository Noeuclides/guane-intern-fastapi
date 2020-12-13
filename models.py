from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


# class User(Base):
#     __tablename__ = 'user'
#     id = Column(String, primary_key=True)
#     first_name = Column(String)
#     last_name = Column(String)
#     username = Column(String)
#     email = Column(String)
#     dog = relationship("Dog", backref="user")

class Dog(Base):
    __tablename__ = 'dogs'
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    picture = Column(String)
    create_date = Column(String)
    is_adopted = Column(String)
    #user_id = Column(Integer, ForeignKey('user.id'))