from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.engine import base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.sqltypes import Numeric

# from .database import Base
# What is main use of init class


from database import Base




class Register(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, unique=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)


# class Stocks(Base):
#     __tablename__ = "stocks"

#     id = Column(Integer, primary_key=True, index=True)
#     user = Column(ForeignKey(Register.email))
#     symbol = Column(String, unique=True, index=True)
#     price = Column(Numeric(10, 2))
#     forward_eps = Column(Numeric(10, 2))
#     dividend_yield = Column(Numeric(10, 2))
#     ma50 = Column(Numeric(10, 2))
#     ma200 = Column(Numeric(10, 2))


class user_stock(Base):
    __tablename__ = "user_stocks"

    id = Column(Integer, primary_key=True, index=True, )
    symbol = Column(String, unique=False)
    user_email = Column(ForeignKey(Register.email))
    

class stocks_symbols(Base):
    __tablename__ = "stocks Symbols"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True)

    





