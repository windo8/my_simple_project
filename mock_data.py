import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker
from sqlalchemy.future import select
from core.database import get_db  
from api.models.user import User 
from api.models.board import Board 
from api.models.comment import Comment

fake = Faker()

async def create_fake_data(num_users=1000, num_boards=50000, num_comments=200000):
    async for session in get_db():  # get_db()를 통해 db 세션을 가져옴
        # 가상 사용자 데이터 생성
        users = []
        generated_usernames = set()
        generated_emails = set()
        
        for _ in range(num_users):
            username = fake.user_name()
            email = fake.email()
            
            # 중복된 username을 피하기 위해 재생성
            while username in generated_usernames:
                username = fake.user_name()
            while email in generated_emails:
                email = fake.email()
            
            generated_usernames.add(username)
            generated_emails.add(email)
            
            
            user = User(
                username=username,
                email=email,
                hashed_password=fake.password(),
                gender=fake.boolean(),
                age=fake.random_int(min=18, max=80)
            )
            session.add(user)
            users.append(user)
        
        await session.flush()  # 세션에 있는 사용자 데이터를 DB에 적용하여 ID 생성

        # 가상 게시판 데이터 생성
        boards = []
        for _ in range(num_boards):
            board = Board(
                user_id=fake.random_element(users).id,  # 랜덤한 사용자 선택
                title=fake.sentence(),
                content=fake.paragraph(),
                is_visible=fake.boolean(),
                thumbnail=fake.image_url()
            )
            session.add(board)
            boards.append(board)
        
        await session.flush()  # 세션에 있는 게시판 데이터를 DB에 적용하여 ID 생성

        # 가상 댓글 데이터 생성
        for _ in range(num_comments):
            comment = Comment(
                user_id=fake.random_element(users).id,  # 랜덤한 사용자 선택
                board_id=fake.random_element(boards).id,  # 랜덤한 게시판 선택
                content=fake.sentence(),
                comment_seq=fake.random_int(min=1, max=10),
                comment_num=fake.random_int(min=1, max=100)
            )
            session.add(comment)

        # 세션 커밋은 get_db에서 자동으로 처리됨

async def main():
    await create_fake_data()

if __name__ == "__main__":
    asyncio.run(main())