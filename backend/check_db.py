import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy.future import select
from app.models.supervisor import Supervisor
from app.models.teacher import Teacher

async def check():
    async with AsyncSessionLocal() as s:
        r = await s.execute(select(Supervisor))
        users = r.scalars().all()
        print(f"Total supervisors: {len(users)}")
        for u in users:
            print(f"  id={u.id} username={u.username} hashed_pw={u.hashed_password[:40]}...")
        
        r2 = await s.execute(select(Teacher))
        teachers = r2.scalars().all()
        print(f"Total teachers: {len(teachers)}")

asyncio.run(check())
