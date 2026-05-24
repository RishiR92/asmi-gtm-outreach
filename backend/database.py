from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# In production (Railway) point to the persistent volume; locally use the repo file
_default_db = os.path.join(BASE_DIR, "outreach.db")
DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{_default_db}"

# Railway gives a postgres:// URL if you add a Postgres plugin — convert if needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
