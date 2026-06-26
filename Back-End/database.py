"""
database.py — PostgreSQL connection via SQLAlchemy

Set your database URL in the .env file:
    DATABASE_URL=postgresql://thd_user:thd_password@localhost:5432/thd_hr
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://thd_user:thd_password@localhost:5432/thd_hr"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # Re-establish broken connections automatically
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency — yields a database session and closes it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
