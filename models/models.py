from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
    pass

class BaseModel:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Base(DeclarativeBase):
    pass

class User(Base, BaseModel):
    __tablename__ = 'User'
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username:Mapped[str] = mapped_column(String(200), unique=True)
    email:Mapped[str] = mapped_column(String(120), unique=True)
    password:Mapped[str] = mapped_column(String(255))


class Expenses(Base, BaseModel):
    __tablename__ = 'Expenses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('User.id'))  
    date: Mapped[datetime] = mapped_column(DateTime)
    description: Mapped[str] = mapped_column(String(64))
    amount: Mapped[str] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(64))

class Income(Base, BaseModel):
    __tablename__ = 'Income'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('User.id'))  
    date: Mapped[datetime] = mapped_column(DateTime)
    source: Mapped[str] = mapped_column(String(64))
    amount: Mapped[str] = mapped_column(Float)
