import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    picture = Column(Text, nullable=False)


class Category(Base):

    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class Item(Base):

    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    added = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

engine = create_engine(
    'postgresql+psycopg2://vagrant:123@localhost/catalog')

Base.metadata.create_all(engine)
