import asyncpg
from config import DATABASE_URL

db_pool = None

async def init_db():
    """Initializes the database connection pool if it hasn't been initialized."""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        async with db_pool.acquire() as connection:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS company (
                    id SERIAL PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL
                );
                CREATE TABLE IF NOT EXISTS department (
                    id SERIAL PRIMARY KEY,
                    department_name VARCHAR(255) NOT NULL,
                    company_id INT REFERENCES company(id) ON DELETE SET NULL
                );
                CREATE TABLE IF NOT EXISTS role (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL
                );
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE NOT NULL,
                    fullname VARCHAR(255),
                    username VARCHAR(255) UNIQUE,
                    phone_number VARCHAR(50),
                    birthdate DATE,
                    lang VARCHAR(5) DEFAULT 'ru',
                    role_id INT REFERENCES role(id) ON DELETE SET NULL,
                    department_id INT REFERENCES department(id) ON DELETE SET NULL,
                    company_id INT REFERENCES company(id) ON DELETE SET NULL,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS project (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    boss_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL
                );
                CREATE TABLE IF NOT EXISTS user_m2m_project (
                    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                    project_id BIGINT REFERENCES project(id) ON DELETE CASCADE,
                    role VARCHAR(50),
                    PRIMARY KEY (user_id, project_id)
                );
                CREATE TABLE IF NOT EXISTS task (
                    id SERIAL PRIMARY KEY,
                    task_title VARCHAR(30) NOT NULL,
                    task_description TEXT,
                    start_date DATE,
                    due_date DATE,
                    status VARCHAR(50),
                    task_owner_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
                    task_assignee_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    paused_at TIMESTAMP,
                    continued_at TIMESTAMP,
                    finished_at TIMESTAMP,
                    project_id INT REFERENCES project(id) ON DELETE SET NULL
                );
            """)

def get_db_pool():
    """Returns the database pool if initialized."""
    if db_pool is None:
        raise Exception("Database pool not initialized. Call init_db() first.")
    return db_pool

async def get_user(telegram_id: int):
    """Fetches a user from the database by telegram ID."""
    if db_pool is None:
        raise Exception("Database pool has not been initialized. Call init_db first.")
    async with db_pool.acquire() as connection:
        user = await connection.fetchrow("SELECT * FROM users WHERE user_id = $1", telegram_id)
        if user is None:
            print(f"[Debug] No user found in DB for telegram_id={telegram_id}")
        return user

async def get_user_lang(telegram_id):
    """Fetches a user's language from the database by telegram ID."""
    async with db_pool.acquire() as connection:
        return await connection.fetchval("SELECT lang FROM users WHERE user_id = $1", telegram_id)