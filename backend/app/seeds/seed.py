import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal, engine
from app.models import Base
from app.models.supervisor import Supervisor
from app.models.teacher import Teacher
from app.models.timetable import TimetableEntry, Weekday
from app.auth.security import get_password_hash
from app.seeds.timetable_data import TEACHERS_DATA, TIMETABLE_RAW, WEEKDAYS, parse_cell

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        # 1. Seed Supervisor (Vaishali / Vaishali)
        existing_supe = (await session.execute(select(Supervisor).where(Supervisor.username == "Vaishali"))).scalar_one_or_none()
        if not existing_supe:
            supe = Supervisor(
                username="Vaishali",
                hashed_password=get_password_hash("Vaishali"),
                full_name="Mrs. Vaishali Patil"
            )
            session.add(supe)
            # Commit immediately: previously this relied on the teacher-seeding
            # branch below to commit, so on a database that already had teachers
            # the supervisor was silently rolled back and login always failed.
            await session.commit()
            print("Supervisor 'Vaishali' created.")
        else:
            print("Supervisor 'Vaishali' already exists.")
        
        # 2. Seed 19 Teachers
        existing_teachers = (await session.execute(select(Teacher))).scalars().all()
        if not existing_teachers:
            teacher_objs = []
            for t_data in TEACHERS_DATA:
                t = Teacher(name=t_data["name"], class_name=t_data["class_name"], active=True)
                teacher_objs.append(t)
                session.add(t)
            await session.flush()
            print(f"Created {len(teacher_objs)} teachers.")
            
            # 3. Seed Timetable for each teacher
            tt_entries = []
            for idx, teacher in enumerate(teacher_objs):
                teacher_timetable = TIMETABLE_RAW.get(idx, {})
                for period_num in range(1, 10):
                    period_days = teacher_timetable.get(period_num, ["-"] * 6)
                    for day_idx, weekday in enumerate(WEEKDAYS):
                        cell = period_days[day_idx] if day_idx < len(period_days) else "-"
                        subject, class_name, is_free = parse_cell(cell)
                        entry = TimetableEntry(
                            teacher_id=teacher.id,
                            weekday=weekday,
                            period_number=period_num,
                            subject=subject,
                            class_name=class_name or teacher.class_name,
                            is_free=is_free,
                            is_recess=False
                        )
                        tt_entries.append(entry)
            
            session.add_all(tt_entries)
            await session.commit()
            print(f"Seeded {len(tt_entries)} timetable entries across 6 days & 9 periods.")
        else:
            print("Teachers already seeded.")

if __name__ == "__main__":
    asyncio.run(seed())
