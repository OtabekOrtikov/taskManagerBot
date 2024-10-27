from aiogram import types

from database.db_utils import get_db_pool

async def delete_db(message: types.Message):
    db_pool = get_db_pool()
    """Deletes all tables from the database."""
    async with db_pool.acquire() as connection:
        await connection.execute("""
            DELETE FROM users;
            DELETE FROM task;
            DELETE FROM user_m2m_project;
            DELETE FROM project;
            DELETE FROM department;
            DELETE FROM company;
        """)
    await message.answer("All tables have been deleted.")