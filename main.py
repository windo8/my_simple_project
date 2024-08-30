from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

from core.database import Base, engine

from api.models.user import User  # 경로는 실제 구조에 맞게 조정하세요
from api.models.board import Board
from api.models.comment import Comment

from api.endpoints.user import user_router
from api.endpoints.board import board_router
from api.endpoints.comment import cmt_router
from api.endpoints.admin import admin_router


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    
    # 종료시 테이블 드랍
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)



# FastAPI 초기화
app = FastAPI(lifespan=app_lifespan)
app.add_middleware(SessionMiddleware, secret_key='your-secret-key')

# 라우터 등록
app.include_router(admin_router, prefix='/admin', tags=['admin'])
app.include_router(user_router ,prefix='/user', tags=['user'])
app.include_router(board_router ,prefix='/board', tags=['board'])
app.include_router(cmt_router ,prefix='/comment', tags=['comment'])


import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)