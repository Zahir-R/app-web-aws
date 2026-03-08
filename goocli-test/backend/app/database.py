import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Expecting AWS RDS PostgreSQL URI, defaulting to local for dev
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost/menopause_db"
)

# Engine is the start point that will enable sqlalchemy to use database
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# Create a session to manage the database for user
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()   # Autodescriptive, but need some DB knowledge

def get_db():
    """
    Return DB step by step, to not wast too much memory
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # When "finally" reach end of db in sessionlocal, close the db
