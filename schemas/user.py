from pydantic import BaseModel # EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    gender: bool
    age: int

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    # email: Optional[EmailStr] = None
    email: Optional[str] = None
    age: Optional[int] = None