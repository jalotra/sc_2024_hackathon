from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = os.environ.get("MYSQL_URL")
if SQLALCHEMY_DATABASE_URL is None:
    print("Not able to find the env var : MYSQL_URL")
    exit(1)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
