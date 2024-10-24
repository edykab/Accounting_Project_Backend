from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Numeric
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class BaseModel:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

class User(Base, BaseModel):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(200), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    
    # Relationships
    expenses: Mapped[List["Expense"]] = relationship(back_populates="user")
    incomes: Mapped[List["Income"]] = relationship(back_populates="user")

class Expense(Base, BaseModel):
    __tablename__ = 'expense'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    description: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(50))
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="expenses")

class Income(Base, BaseModel):
    __tablename__ = 'income'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    source: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="incomes")