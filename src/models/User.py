from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from typing import Union
from ..database import Base


# Entity to model User in the system
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    namespace_id = Column(Integer, ForeignKey("namespace.id"))


class Namespace(Base):
    __tablename__ = "namespace"
    id = Column(Integer, primary_key=True, autoincrement=True)
    namespace_value = Column(
        String(100),
        nullable=False,
    )
    company_id = Column(String(100), nullable=True)
