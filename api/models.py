from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    create_date = Column(String)
    dog = relationship("Dog", backref="user")


class Dog(Base):
    __tablename__ = 'dogs'
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    picture = Column(String)
    create_date = Column(String)
    is_adopted = Column(Boolean)
    user_id = Column(String, ForeignKey('user.id'), nullable=True)
