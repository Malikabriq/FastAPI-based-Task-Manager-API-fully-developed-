import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------
# DATABASE URL
# ---------------------------
DATABASE_URL = 'postgresql://neondb_owner:npg_wrNv5XO2qpZK@ep-little-heart-a1v7rmta-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
# ENGINE & SESSION
# ---------------------------
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------
# BASE (no explicit schema)
# ---------------------------
Base = declarative_base()  # Use default schema (Postgres 'public')

# ---------------------------
# DEPENDENCY
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# RESET DB (drop & recreate tables)
# ---------------------------
def init_db():
    from app.db import models  # import models here to avoid circular import
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete!")

# ---------------------------
# Run directly
# ---------------------------
if __name__ == "__main__":
    init_db()
