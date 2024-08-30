from pydantic import BaseModel
from typing import Optional

class CommentCreate(BaseModel):
    board_id: int
    content: str
    comment_seq: int
    comment_num: int


class CommentUpdate(BaseModel):
    content: Optional[str] = None