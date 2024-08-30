from sqlalchemy import Column, DateTime
from core.database import Base
from sqlalchemy.sql import func

class BaseModel(Base):
    # 이 클래스는 테이블로 생성되지 않음
    __abstract__ = True
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())