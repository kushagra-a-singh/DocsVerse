import logging
import os
import sys

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from backend.app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False},
    )

    db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", ""))
    os.makedirs(db_dir, exist_ok=True)

    with engine.connect() as conn:
        logger.info("Database connection successful")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise RuntimeError(f"Database initialization failed: {str(e)}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """Initialize the database by creating all tables if they don't exist"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def recreate_db():
    """Drop and recreate all database tables"""
    try:
        Base.metadata.drop_all(bind=engine)

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables recreated successfully")
    except Exception as e:
        logger.error(f"Error recreating database: {str(e)}")
        raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
