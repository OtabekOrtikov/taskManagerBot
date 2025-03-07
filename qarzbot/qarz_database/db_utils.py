import asyncpg
from qarz_config import DATABASE_URL

db_pool = None

async def init_db():
    """Initializes the database connection pool if it hasn't been initialized."""
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        async with db_pool.acquire() as connection:
            await connection.execute("""
                                CREATE TABLE IF NOT EXISTS users (
                                    id SERIAL PRIMARY KEY,
                                    user_id BIGINT NOT NULL UNIQUE,
                                    registration_date TIMESTAMP NOT NULL DEFAULT NOW(),
                                    lang VARCHAR(5) NOT NULL DEFAULT 'ru',
                                    fullname TEXT,
                                    phone_number VARCHAR(20),
                                    birthdate DATE,
                                    notification_settings JSON NOT NULL DEFAULT '{}',
                                    filter_settings JSON NOT NULL DEFAULT '{}',
                                    accepted_rules BOOLEAN DEFAULT False
                                );
                                                    
                                CREATE TABLE IF NOT EXISTS debts (
                                    id SERIAL PRIMARY KEY,
                                    debtor_id BIGINT REFERENCES users(id) ON DELETE CASCADE DEFAULT NULL,
                                    borrower_id BIGINT REFERENCES users(id) ON DELETE CASCADE DEFAULT NULL,
                                    draft_name TEXT NOT NULL,
                                    draft_phone VARCHAR(20) NOT NULL,
                                    full_amount INT NOT NULL,
                                    amounts JSON NOT NULL DEFAULT '{}',
                                    paid_amount JSON DEFAULT '{}',
                                    currency VARCHAR(5) NOT NULL DEFAULT 'SUM',
                                    loan_date DATE NOT NULL,
                                    due_date JSON NOT NULL DEFAULT '{}',
                                    comment TEXT,
                                    status VARCHAR(10) NOT NULL DEFAULT 'draft',
                                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                                );
                                     
                                CREATE TABLE IF NOT EXISTS Company (
                                    id SERIAL PRIMARY KEY,
                                    company_name TEXT NOT NULL,
                                    company_phone VARCHAR(20) NOT NULL,
                                    responsible_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
                                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                                );
                                     
                                CREATE TABLE IF NOT EXISTS Debts4B (
                                    id SERIAL PRIMARY KEY,
                                    debtor_id BIGINT REFERENCES Company(id) ON DELETE CASCADE,
                                    borrower_id BIGINT REFERENCES Company(id) ON DELETE CASCADE,
                                    due_date DATE NOT NULL,
                                    created_date DATE NOT NULL DEFAULT NOW()
                                );
                                                    
                                CREATE TABLE IF NOT EXISTS Transactions (
                                    id SERIAL PRIMARY KEY,
                                    debt_id BIGINT REFERENCES Debts4B(id) ON DELETE CASCADE,
                                    item_name TEXT NULL DEFAULT NULL,
                                    measure_type VARCHAR(15) NULL DEFAULT NULL,
                                    quantity DECIMAL(8,2) NULL DEFAULT NULL,
                                    price DECIMAL(8,2) NULL DEFAULT NULL,
                                    total DECIMAL(8,2) NOT NULL,
                                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                                );
            """)


def get_db_pool():
    """Returns the database pool if initialized."""
    if db_pool is None:
        raise Exception("Database pool not initialized. Call init_db() first.")
    return db_pool

async def get_user(user_id):
    """Returns the user with the given user_id."""
    async with get_db_pool().acquire() as connection:
        return await connection.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    
async def get_company(user_id):
    async with get_db_pool().acquire() as connection:
        return await connection.fetchrow("SELECT * FROM Company WHERE responsible_id = $1", user_id)
    
async def add_new_user(user_id):
    async with get_db_pool().acquire() as connection:
        await connection.execute("INSERT INTO users (user_id) VALUES ($1)", user_id)

async def get_user_lang(user_id):
    """Returns the language of the user with the given user_id."""
    user = await get_user(user_id)
    return user["lang"]

async def get_debt(debt_id: int):
    async with get_db_pool().acquire() as connection:
        return await connection.fetchrow("SELECT * FROM debts WHERE id = $1", debt_id)
    
async def get_user_by_id(id: int):
    async with get_db_pool().acquire() as connection:
        return await connection.fetchrow("SELECT * FROM users WHERE id = $1", id)