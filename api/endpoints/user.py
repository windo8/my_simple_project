from fastapi import Depends, HTTPException, APIRouter, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from schemas.user import UserCreate, UserLogin, UserUpdate
from services.user import UserService

user_router = APIRouter()

@user_router.post('/signup')
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService.signup(user, db)

@user_router.post('/login')
async def login(request: Request, signin: UserLogin, db: AsyncSession = Depends(get_db)):
    user_data = await UserService.login(signin, db)
    request.session['username'] = user_data['username']
    request.session['user_id'] = user_data['user_id']
    return {'message': 'Logged in successfully'}

@user_router.post('/logout')
async def logout(request: Request):
    request.session.clear()
    return {'message': 'Logged out successfully'}


@user_router.patch('/update')
async def update(request: Request, user: UserUpdate, db: AsyncSession=Depends(get_db)):
    user_id = request.session.get('user_id')
    return await UserService.update(user_id=user_id, data=user, db=db)


@user_router.delete('/quit')
async def quit(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get('user_id')
    
    if not user_id:
        raise HTTPException(status_code=401, detail='Login required')
    
    return await UserService.secession(user_id, db)
