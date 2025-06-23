from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declared_attr
from db import Base, engine


class BaseColumnsMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, nullable=False, default=datetime.utcnow)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(BaseColumnsMixin, Base):
    __tablename__ = 'users'

    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)


def create_db():
    Base.metadata.create_all(engine)
