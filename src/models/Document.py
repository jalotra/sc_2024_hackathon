from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from typing import Union
from ..database import Base


# Entity to model uploaded Documents
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    namespace_id = Column(Integer, ForeignKey("namespace.id"), nullable=False)
    redis_document_id = Column(String(10000), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_parsed = Column(Boolean, nullable=True)


class RedisDocument(BaseModel):
    key: str
    value: str | bytes
