from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from api.models.user import User
from schemas.user import UserCreate, UserLogin, UserUpdate
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    
    @staticmethod
    async def signup(user: UserCreate, db: AsyncSession):
        try:
            # 이메일 중복 검사
            result = await db.execute(select(User).where(User.email == user.email))
            if result.scalars().first():
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # 사용자 이름 중복 검사
            result = await db.execute(select(User).where(User.username == user.username))
            if result.scalars().first():
                raise HTTPException(status_code=400, detail="Username already taken")
            
            # 새 사용자 객체 생성
            hashed_password = pwd_context.hash(user.password)
            new_user = User(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password,
                gender=user.gender,
                age=user.age
            )
            
            # 데이터베이스에 사용자 추가
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            return {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "gender": new_user.gender,
                "age": new_user.age
            }
        
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Database integrity error")
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error")


    @staticmethod
    async def login(signin: UserLogin, db: AsyncSession):
        result = await db.execute(select(User).where(User.username == signin.username))
        user = result.scalars().first()
        
        if user and pwd_context.verify(signin.password, user.hashed_password):
            return {
                'username': user.username,
                'user_id': user.id
            }
        else:
            raise HTTPException(status_code=401, detail='Login failed')


    @staticmethod
    async def update(user_id: int, data: UserUpdate, db: AsyncSession):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=401, detail='User not fount')
        
        if data.email is not None:
            user.email = data.email
        if data.age is not None:
            user.age = data.age
        
        try:
            await db.commit()
            await db.refresh(user)
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(status_code=500, detail='Update failed')
        
        return {'message': 'User successfully updated'}


    @staticmethod
    async def secession(user_id: int, db: AsyncSession):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
    
        if not user:
            raise HTTPException(status_code=401, detail='User not found')
        
        try: 
            await db.delete(user)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(status_code=500, detail='Deletion failed')
        
        return {'message': 'User successfully deleted'}
