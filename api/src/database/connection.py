from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.database.config import settings

SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI


engine = create_engine(
    str(SQLALCHEMY_DATABASE_URL)
)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()