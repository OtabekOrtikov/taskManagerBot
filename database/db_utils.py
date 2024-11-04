import asyncpg
from config import DATABASE_URL
from utils.priority_parser import parse_priority_id

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
                    company_id INT REFERENCES company(id) ON DELETE SET NULL,
                    status VARCHAR(50) DEFAULT 'active'
                );

                CREATE TABLE IF NOT EXISTS role (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL
                );
                                     
                INSERT INTO role (id, name) VALUES (1, 'Boss'), (2, 'Manager'), (3, 'Worker') ON CONFLICT DO NOTHING;

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
                    project_name VARCHAR(255) NOT NULL,
                    boss_id BIGINT REFERENCES users(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS user_m2m_project (
                    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
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
                    task_owner_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
                    task_assignee_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
                    priority VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    paused_at TIMESTAMP,
                    continued_at TIMESTAMP,
                    finished_at TIMESTAMP,
                    canceled_at TIMESTAMP,
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
        return user

async def get_user_lang(telegram_id):
    """Fetches a user's language from the database by telegram ID."""
    async with db_pool.acquire() as connection:
        return await connection.fetchval("SELECT lang FROM users WHERE user_id = $1", telegram_id)
    
async def add_user_with_role(connection, telegram_id, username, role_id, company_id, department_id):
    """Adds a user to the database with a specified role."""
    await connection.execute("INSERT INTO users (user_id, username, role_id, company_id, department_id) VALUES ($1, $2, $3, $4, $5)", telegram_id, username, role_id, company_id, department_id)

async def get_department_manager(connection, company_id, department_id):
    """Checks if a Manager exists for the specified department."""
    return await connection.fetchval("SELECT id FROM users WHERE company_id = $1 AND department_id = $2 AND role_id = 2", company_id, department_id)

async def create_task(connection, task_title, task_description, start_date, due_date, task_owner_id, task_assignee_id, priority, project_id, created_at):
    """Creates a task in the database."""
    priority_id = await parse_priority_id(priority)
    if project_id:
        await connection.execute("""
            INSERT INTO task (
                task_title, 
                task_description, 
                start_date, 
                due_date, 
                status, 
                task_owner_id, 
                task_assignee_id, 
                priority, 
                project_id,
                created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
            task_title,
            task_description,
            start_date,
            due_date,
            'Not started',
            task_owner_id,
            task_assignee_id,
            priority_id,
            project_id,
            created_at)
    else:
        await connection.execute("""
            INSERT INTO task (
                task_title, 
                task_description, 
                start_date, 
                due_date, 
                status, 
                task_owner_id, 
                task_assignee_id, 
                priority,
                created_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
            task_title,
            task_description,
            start_date,
            due_date,
            'Not started',
            task_owner_id,
            task_assignee_id,
            priority_id,
            created_at)
        
async def get_task_with(connection, task_id):
    """Fetches a task with the project name."""
    return await connection.fetchrow("""
        SELECT t.*, p.project_name
        FROM task t
        LEFT JOIN project p ON t.project_id = p.id
        WHERE t.id = $1
    """, task_id)