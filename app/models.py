from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, select, func
from sqlalchemy.ext.hybrid import hybrid_property
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
    comments = relationship("Comment", back_populates="author")


class Post(BaseColumnsMixin, Base):
    __tablename__ = "posts"

    title = Column(String(length=100), unique=True, nullable=False)
    body = Column(Text, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    
    @hybrid_property
    def comments_count(self):
        return len(self.comments)
    
    @comments_count.expression
    def comments_count(cls):
        return (
            select(func.count(Comment.id))
            .where(Comment.post_id == cls.id)
            .scalar_subquery()
        )


class Comment(BaseColumnsMixin, Base):
    __tablename__ = "comments"

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")


def create_db():
    Base.metadata.create_all(engine)
