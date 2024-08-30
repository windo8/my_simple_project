from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.templating import Jinja2Templates

from sqlalchemy import case, func, desc
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from api.models.user import User
from api.models.board import Board
from api.models.comment import Comment

from services.board import BoardService
from services.board import BoardService
from services.user import UserService


admin_router = APIRouter()


@admin_router.get('/is_visible')
async def exam1(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            User.gender,
            func.count(Board.id).label('비공개_게시물_수')
        )
        .join(Board, User.id == Board.user_id)
        .where(Board.is_visible == 0)
        .group_by(User.gender)
    )
    
    # 결과를 가져와서 리스트로 변환
    data = result.fetchall()  # 또는 result.all()로 사용할 수 있습니다.

    # 결과를 딕셔너리 형태로 변환
    data_dict = [{'gender': key, '비공개_게시물_수': value} for key, value in data]

    return {'data': data_dict}


@admin_router.get('/average_age')
async def exam2(db: AsyncSession=Depends(get_db)):
    result = await db.execute(
        select(
            User.gender,
            func.avg(User.age).label('평균나이')
        )
        .group_by(User.gender)
    )
    
    data = result.fetchall()
    
    data_dict = [{'gender': key, '평균나이': value} for key, value in data]
    
    return {'data': data_dict}


@admin_router.get('/max_comment_post')
async def exam3(db: AsyncSession=Depends(get_db)):
    result = await db.execute(
        select(
            Board.title,
            func.count(Comment.id).label('댓글 수')
        )
        .join(Comment, Board.id == Comment.board_id)
        .group_by(Board.title)
        .order_by(desc('댓글 수'))
        .limit(100)
    )
    data = result.fetchall()
    
    data_dict = [{'title': key, '댓글 수': value} for key, value in data]
    
    return {'data': data_dict}


@admin_router.get('/outer_join')
async def exam4(db: AsyncSession = Depends(get_db)):
    # 서브쿼리로 유저별 작성한 게시물 수 계산
    subquery_boards = (
        select(
            Board.user_id,
            func.count(Board.id).label('작성한_게시물_수')
        )
        .group_by(Board.user_id)
        .subquery() # <================ subquery
    )
    
    # 서브쿼리로 유저별 작성한 댓글 수 계산
    subquery_comments = (
        select(
            Comment.user_id,
            func.count(Comment.id).label('작성한_댓글_수')
        )
        .group_by(Comment.user_id)
        .subquery()
    )
    
    # 메인 쿼리: 유저 정보와 위 두 서브쿼리를 조인하여 결과 도출
    result = await db.execute(
        select(
            User.username,
            func.coalesce(subquery_boards.c.작성한_게시물_수, 0).label('작성한_게시물_수'),
            func.coalesce(subquery_comments.c.작성한_댓글_수, 0).label('작성한_댓글_수')
        )
        .outerjoin(subquery_boards, User.id == subquery_boards.c.user_id)
        .outerjoin(subquery_comments, User.id == subquery_comments.c.user_id)
        .order_by(desc('작성한_게시물_수'))
        .limit(10)
    )
    # - coalesce 는 NULL 값을 다른 값으로 대체할 때 유용합니다.
    # - outer join 은 조인할 때 양쪽 테이블에서 일치하지 않는 행도 포함하고 싶을 때 사용됩니다.
    
    data = result.fetchall()
    
    return [{'username': k, '작성한_게시물_수': v1, '작성한_댓글_수': v2} for k, v1, v2 in data]


@admin_router.get('/case')
async def exam5(db: AsyncSession=Depends(get_db)):
    result = await db.execute(
        select(
            User.username,
            # 공개 게시물 수 계산
            func.sum(
                case(
                    (Board.is_visible == 1, 1),  # 조건: Board의 is_visible 필드가 1일 때 1을 반환
                    else_=0  # 그 외의 경우에는 0을 반환
                )
            ).label('공개_게시물_수'),  # 이 결과를 '공개_게시물_수'로 라벨링
            # 비공개 게시물 수 계산
            func.sum(
                case(
                    (Board.is_visible == 0, 1),
                    else_=0
                )
            ).label('비공개_게시물_수')
        )
        .join(Board, User.id == Board.user_id)  # User와 Board 테이블을 user_id를 기준으로 조인
        .group_by(User.username)
        .limit(10)
    )
    
    # 쿼리 결과를 fetchall()로 가져옴
    data = result.fetchall()
    
    return [{'username': k, '공개_게시물_수': v1, '비공개_게시물_수': v2} for k, v1, v2 in data]


