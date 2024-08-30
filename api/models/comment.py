from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

from api.models.base_table import BaseModel

class Comment(BaseModel):
    __tablename__ = 'comment'
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    board_id = Column(Integer, ForeignKey('board.id'))
    
    content = Column(String(228), nullable=False)
    comment_seq = Column(Integer)
    comment_num = Column(Integer)
    
    # Comment와 User의 관계 설정 (N:1)
    user = relationship("User", back_populates="comments")
    # Comment와 Board의 관계 설정 (N:1)
    board = relationship("Board", back_populates="comments")


