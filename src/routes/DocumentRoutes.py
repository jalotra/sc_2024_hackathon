from ..database import SessionLocal, engine
from sqlalchemy.orm import Session
from ..models.Document import Document
from typing import Optional
from ..redis_database import pool
import logging
from fastapi import Depends
from redis import Redis
import uuid
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ..models.Document import RedisDocument
import redis
import src.models.Document as DocumentBase

DocumentBase.Base.metadata.create_all(bind=engine)
document_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis_db():
    redis_connection = redis.Redis(connection_pool=pool)
    try:
        yield redis_connection
    except Exception as e:
        raise e


def read_redis_document(redis_conn: Redis, document_key: str):
    return RedisDocument(value=redis_conn.get(document_key), key=document_key)


def create_redis_document(
    redis_conn: Redis, document_key: Optional[str], document_value: str
):
    if document_key is None:
        redis_document_id = str(uuid.uuid4())
        redis_conn.set(redis_document_id, document_value)
        return redis_document_id
    else:
        redis_conn.set(document_key, document_value)
        return document_key

def create_redis_document_set(
    redis_conn: Redis, document_key: str, document_value: str
):
    document_key = "SET_" + document_key
    """Puts a document_value inside a set with key document_key"""
    redis_conn.sadd(document_key, document_value)
    return document_key


# Create Document
def create_document(
    db: Session,
    namespace_id: str,
    redis_document_id: int,
    user_id: int,
    is_parsed: Optional[bool] = None,
):
    db_document = Document(
        namespace_id=namespace_id,
        redis_document_id=redis_document_id,
        user_id=user_id,
        is_parsed=is_parsed,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


# Read Document
def read_document(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def match_document(db : Session, document_name : str):
    """Matches a name of document to all the documents"""
    pattern = f"%{document_name}%"
    return db.query(Document).filter(Document.redis_document_id.like(pattern)).all()


# Update Document
def update_document(
    db: Session,
    document_id: int,
    namespace: str,
    redis_document_id: int,
    user_id: int,
    is_parsed: Optional[bool] = None,
):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document:
        db_document.namespace = namespace
        db_document.redis_document_id = redis_document_id
        db_document.user_id = user_id
        db_document.is_parsed = is_parsed
        db.commit()
        return db_document
    return None


# Delete Document
def delete_document(db: Session, document_id: int):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document:
        db.delete(db_document)
        db.commit()
        return True
    return False


@document_router.post("/documents", response_model=dict)
def create_document_endpoint(
    redis_document: RedisDocument,
    namespace_id: str,
    user_id: int,
    is_parsed: Optional[bool] = None,
    db: Session = Depends(get_db),
    redis_pool=Depends(get_redis_db),
):
    redis_document_id = create_redis_document(redis_pool, redis_document.value)
    print(redis_document_id)
    db_document = create_document(
        db,
        namespace_id=namespace_id,
        redis_document_id=redis_document_id,
        user_id=user_id,
        is_parsed=False,
    )
    return JSONResponse(content=jsonable_encoder(db_document))


@document_router.get("/documents/{document_id}", response_model=dict)
def read_document_endpoint(document_id: int, db: Session = Depends(get_db)):
    db_document = read_document(db, document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return JSONResponse(content=jsonable_encoder(db_document))


@document_router.put("/documents/{document_id}", response_model=dict)
def update_document_endpoint(
    document_id: int,
    namespace: str,
    redis_document_id: int,
    user_id: int,
    is_parsed: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    db_document = update_document(
        db, document_id, namespace, redis_document_id, user_id, is_parsed
    )
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return JSONResponse(content=jsonable_encoder(db_document))


@document_router.delete("/documents/{document_id}", response_model=dict)
def delete_document_endpoint(document_id: int, db: Session = Depends(get_db)):
    success = delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted"}
