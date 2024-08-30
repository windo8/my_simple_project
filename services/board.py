from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from api.models.board import Board
from schemas.board import BoardCreate, BoardUpdate


class BoardService:
    
    @staticmethod
    async def save(user_id: int, data: BoardCreate, db: AsyncSession):
        board = Board(
            user_id=user_id,
            title=data.title,
            content=data.content,
            is_visible=data.is_visible,
            thumbnail=data.thumbnail
        )
        db.add(board)
        try:
            await db.commit()
            await db.refresh(board)
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to save the board")
        return board
    
    
    @staticmethod
    async def find_post_info(board_id: int, db: AsyncSession):
        result = await db.execute(
            select(Board)
            .options(joinedload(Board.user), joinedload(Board.comments))
            .where(Board.id == board_id)
        )
        post = result.scalars().first()
        
        return post  # 서비스는 데이터를 반환만 함
    
    
    @staticmethod
    async def find_by_id(board_id: int, db: AsyncSession):
        result = await db.execute(select(Board).where(Board.id == board_id))
        board = result.scalars().first()
        return board
    
    
    @staticmethod
    async def edit(board_id: int, data: BoardUpdate, db: AsyncSession):
        # Get the board by ID
        board = await BoardService.find_by_id(board_id, db)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Update the board fields
        if data.title is not None:
            board.title = data.title
        if data.content is not None:
            board.content = data.content
        if data.is_visible is not None:
            board.is_visible = data.is_visible
        
        try:
            await db.commit()  # Commit the changes to the database
            await db.refresh(board)  # Refresh the instance with the latest data from the DB
        except SQLAlchemyError:
            await db.rollback()  # Rollback in case of an error
            raise HTTPException(status_code=500, detail="Failed to edit the board")
        
        return board  # Return the updated board object
    
    
    @staticmethod
    async def delete(board_id: int, db: AsyncSession):
        board = await BoardService.find_by_id(board_id, db)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        try:
            await db.delete(board)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete the board")
        
        return board
