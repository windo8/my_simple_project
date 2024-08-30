from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

from api.models.base_table import BaseModel

class Board(BaseModel):
    __tablename__ = 'board'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    
    title = Column(String(512), nullable=True)
    content = Column(String(1028), nullable=True)
    is_visible = Column(Boolean, default=0)
    thumbnail = Column(String(512), nullable=True)
    
    # Board와 User의 관계 설정 (N:1)
    user = relationship("User", back_populates="boards")
    # Board와 Comment의 관계 설정 (1:N)
    comments = relationship("Comment", back_populates="board", cascade="all, delete-orphan")