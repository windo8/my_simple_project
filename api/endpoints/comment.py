from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.templating import Jinja2Templates

from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from api.models.comment import Comment
from schemas.comment import CommentCreate, CommentUpdate


cmt_router = APIRouter()


@cmt_router.post('/')
async def write_cmt(request: Request, cmt: CommentCreate, db: AsyncSession=Depends(get_db)):
    user_id = request.session.get('user_id')
    try:
        new_cmt = Comment(
            user_id = user_id,
            board_id = cmt.board_id,
            content = cmt.content,
            comment_seq = cmt.comment_seq,
            comment_num = cmt.comment_num
        )
        db.add(new_cmt)
        await db.commit()
        await db.refresh(new_cmt)
        
        return new_cmt
    
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database integrity error")
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


@cmt_router.patch('/{comment_id}')
async def update(request: Request, comment_id: int, data: CommentUpdate, db: AsyncSession=Depends(get_db)):
    user_id = request.session.get('user_id')
    
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    
    if not comment:
        raise HTTPException(status_code=401, detail='Comment not found')
    
    if comment.user_id != user_id:
        raise HTTPException(status_code=401, detail='Login pleass')
    
    if data.content is not None:
        comment.content = data.content
    
    await db.commit()
    await db.refresh(comment)
    return {'message': 'Successfully updated comment', 'commten': comment}