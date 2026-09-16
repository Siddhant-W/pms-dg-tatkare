import pytest
from app.models.teacher import Teacher
from app.models.supervisor import Supervisor
from app.services.favorites import list_favorites, add_favorite, remove_favorite
from app.tests.conftest import TestSessionLocal


@pytest.mark.asyncio
async def test_favorites_add_list_remove_idempotent():
    async with TestSessionLocal() as db:
        supe = Supervisor(username="fav_test")
        teacher = Teacher(name="Favorite Candidate")
        db.add_all([supe, teacher])
        await db.commit()
        supe_id = supe.id
        teacher_id = teacher.id

    async with TestSessionLocal() as db:
        favs = await list_favorites(db, supe_id)
        assert favs == []

    # Adding twice must not error or duplicate.
    async with TestSessionLocal() as db:
        await add_favorite(db, supe_id, teacher_id)
    async with TestSessionLocal() as db:
        await add_favorite(db, supe_id, teacher_id)

    async with TestSessionLocal() as db:
        favs = await list_favorites(db, supe_id)
        assert len(favs) == 1
        assert favs[0].teacher_id == teacher_id
        assert favs[0].teacher_name == "Favorite Candidate"

    # Removing twice must not error either.
    async with TestSessionLocal() as db:
        await remove_favorite(db, supe_id, teacher_id)
    async with TestSessionLocal() as db:
        await remove_favorite(db, supe_id, teacher_id)

    async with TestSessionLocal() as db:
        favs = await list_favorites(db, supe_id)
        assert favs == []
