from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)

sessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

def get_db():
    """
    Dependency to get the database session.
    """
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
