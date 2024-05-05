from contextlib import contextmanager

from .connection import SessionLocal


def create_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_db = contextmanager(create_session)
