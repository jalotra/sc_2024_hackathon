from ..database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from ..models.User import User, Namespace
from fastapi.exceptions import HTTPException
from typing import Optional
from ..models.User import User
import src.models.User as UserBase
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

UserBase.Base.metadata.create_all(bind=engine)
user_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create User
def create_user(db: Session, namespace_id: int):
    db_user = User(namespace_id=namespace_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Read User
def read_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# Update User
def update_user(db: Session, user_id: int, namespace_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.namespace_id = namespace_id
        db.commit()
        return db_user
    return None


# Delete User
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# Create Namespace
def create_namespace(
    db: Session, namespace_value: str, company_id: Optional[str] = None
):
    db_namespace = Namespace(namespace_value=namespace_value, company_id=company_id)
    db.add(db_namespace)
    db.commit()
    db.refresh(db_namespace)
    return db_namespace


# Read Namespace
def read_namespace(db: Session, namespace_id: int):
    return db.query(Namespace).filter(Namespace.id == namespace_id).first()


# Update Namespace
def update_namespace(
    db: Session,
    namespace_id: int,
    namespace_value: str,
    company_id: Optional[str] = None,
):
    db_namespace = db.query(Namespace).filter(Namespace.id == namespace_id).first()
    if db_namespace:
        db_namespace.namespace_value = namespace_value
        db_namespace.company_id = company_id
        db.commit()
        return db_namespace
    return None


# Delete Namespace
def delete_namespace(db: Session, namespace_id: int):
    db_namespace = db.query(Namespace).filter(Namespace.id == namespace_id).first()
    if db_namespace:
        db.delete(db_namespace)
        db.commit()
        return True
    return False


# API Endpoints
@user_router.post("/users/", response_model=dict)
def create_user_endpoint(namespace_id: int, db: Session = Depends(get_db)):
    return JSONResponse(content=jsonable_encoder(create_user(db, namespace_id)))


@user_router.get("/users/{user_id}", response_model=dict)
def read_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = read_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content=jsonable_encoder(db_user))


@user_router.put("/users/{user_id}", response_model=dict)
def update_user_endpoint(
    user_id: int, namespace_id: int, db: Session = Depends(get_db)
):
    db_user = update_user(db, user_id, namespace_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content=jsonable_encoder(db_user))


@user_router.delete("/users/{user_id}", response_model=dict)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}


@user_router.post("/namespaces/", response_model=dict)
def create_namespace_endpoint(
    namespace_value: str,
    company_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    namespace = create_namespace(db, namespace_value, company_id)
    return JSONResponse(content=jsonable_encoder(namespace))


@user_router.get("/namespaces/{namespace_id}", response_model=dict)
def read_namespace_endpoint(namespace_id: int, db: Session = Depends(get_db)):
    db_namespace = read_namespace(db, namespace_id)
    if db_namespace is None:
        raise HTTPException(status_code=404, detail="Namespace not found")
    return JSONResponse(content=jsonable_encoder(db_namespace))


@user_router.put("/namespaces/{namespace_id}", response_model=dict)
def update_namespace_endpoint(
    namespace_id: int,
    namespace_value: str,
    company_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    db_namespace = update_namespace(db, namespace_id, namespace_value, company_id)
    if db_namespace is None:
        raise HTTPException(status_code=404, detail="Namespace not found")
    return JSONResponse(content=jsonable_encoder(db_namespace))


@user_router.delete("/namespaces/{namespace_id}", response_model=dict)
def delete_namespace_endpoint(namespace_id: int, db: Session = Depends(get_db)):
    success = delete_namespace(db, namespace_id)
    if not success:
        raise HTTPException(status_code=404, detail="Namespace not found")
    return {"message": "Namespace deleted"}
