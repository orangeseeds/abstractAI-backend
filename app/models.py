from __future__ import annotations
from passlib.context import CryptContext
from .database import Base
from sqlalchemy import TIMESTAMP, Column, String, Boolean
from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
from sqlalchemy import ForeignKey

# from sqlalchemy.orm import relationship
# from sqlalchemy import Integer
# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    user_name = Column(String(256), nullable=False)
    email = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False)


class Summary(Base):
    __tablename__ = "summaries"
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    request = Column(String, nullable=False)
    response = Column(String, nullable=False)
    domain = Column(String, nullable=False, default=True)
    createdAt = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    # requester = relationship('User', foreign_keys='User.id')
    user_id = Column(ForeignKey("users.id"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
