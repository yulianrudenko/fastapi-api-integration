from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql import func

from .db import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(length=100), nullable=False, unique=True)
    name = Column(String(length=100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
