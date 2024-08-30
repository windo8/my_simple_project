from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from core.database import Base

from api.models.base_table import BaseModel


class User(BaseModel):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True)
    hashed_password = Column(String(512), nullable=False)
    gender = Column(Boolean)
    age = Column(Integer)
    
    # User와 Board의 관계 설정 (1:N)
    boards = relationship("Board", back_populates="user", cascade="all, delete-orphan")
    # User와 Comment의 관계 설정 (1:N)
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
