from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
import uuid
from sqlalchemy import Boolean
from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from dotenv import load_dotenv
import os

# ---------------- DATABASE CONFIG ----------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


# ---------------- SESSION ----------------
async def get_async_session():
    async with async_session_maker() as session:
        yield session


# ---------------- CREATE TABLES ----------------
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ---------------- USER ----------------


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)


# ---------------- FASTAPI USERS DB ----------------
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


# ---------------- POST ----------------
class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    caption = Column(String, nullable=True)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)

    user_id = Column(String, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    comments = relationship("Comment", back_populates="post", cascade="all, delete")
    likes = relationship("Like", back_populates="post", cascade="all, delete")


# ---------------- LIKE ----------------
class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    post_id = Column(String, ForeignKey("posts.id"))

    post = relationship("Post", back_populates="likes")


# ---------------- COMMENT ----------------
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    content = Column(String)
    user_id = Column(String)
    post_id = Column(String, ForeignKey("posts.id"))

    post = relationship("Post", back_populates="comments")