from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    money = Column(Integer, nullable=False, default=100)
    session_id = Column(String, unique=True)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    symbol = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)

# class Profile(Base):
#     __tablename__ = 'profile'
#     id = Column(Integer, primary_key=True)
#
#
# class Stock(Base):
#     __tablename__ = 'stock'
#     id = Column(Integer, primary_key=True)
