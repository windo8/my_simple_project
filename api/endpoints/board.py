from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.templating import Jinja2Templates

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from api.models.board import Board

from schemas.board import BoardCreate, BoardUpdate
from services.board import BoardService


board_router = APIRouter()


@board_router.post('/')
async def create_board(request: Request, data: BoardCreate, db: AsyncSession=Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    board = await BoardService.save(user_id=user_id, data=data, db=db)
    return {"message": "게시물이 성공적으로 생성되었습니다.", "board": board}


@board_router.get('/{board_id}')
async def get_board(board_id: int, db: AsyncSession=Depends(get_db)):
    post = await BoardService.find_post_info(board_id, db)
    
    if not post:
        raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다.")
    
    return {
        'user': {
            'id': post.user.id,
            'username': post.user.username,
            'email': post.user.email
        },
        'board': {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'is_visible': post.is_visible,
            'thumbnail': post.thumbnail
        },
        'comments': [
            {
                'id': comment.id,
                'content': comment.content,
                'comment_seq': comment.comment_seq,
                'comment_num': comment.comment_num
            } for comment in post.comments
        ]
    }



@board_router.patch('/{board_id}')
async def update_board(board_id: int, data: BoardUpdate, db: AsyncSession = Depends(get_db)):
    board = await BoardService.edit(
        board_id=board_id,
        data=data,
        db=db
    )
    return {"message": "게시물이 성공적으로 수정되었습니다.", "board": board}



@board_router.delete('/{board_id}')
async def delete_board(board_id: int, db: AsyncSession=Depends(get_db)):
    board = await BoardService.find_by_id(board_id, db)
    if not board:
        raise HTTPException(status_code=404, detail="게시물을 찾을 수 없습니다.")
    
    await BoardService.delete(board_id=board_id, db=db)
    return {"message": "게시물이 성공적으로 삭제되었습니다."}