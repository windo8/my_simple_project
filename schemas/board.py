from pydantic import BaseModel
from typing import Optional

class BoardCreate(BaseModel):
    title: str
    content: str
    is_visible: bool
    thumbnail: str

class BoardUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_visible: Optional[bool] = None
