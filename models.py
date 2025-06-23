from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declared_attr, relationship
from db import Base, engine


class BaseColumnsMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, nullable=False, default=datetime.utcnow)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
        )


class User(BaseColumnsMixin, Base):
    __tablename__ = "users"

    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)

    posts = relationship("Post", back_populates="author")


class Post(BaseColumnsMixin, Base):
    __tablename__ = "posts"

    title = Column(String(length=100), unique=True, nullable=False)
    body = Column(Text, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    author = relationship("User", back_populates="posts")


def create_db():
    Base.metadata.create_all(engine)
