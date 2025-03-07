import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncpg
import asyncio
from decimal import Decimal
from datetime import datetime

API_TOKEN = '7933972214:AAFnpcEYmsdjmoPj0D2BSAY-KQucH45sac0'  # Укажите ваш токен

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Глобальная переменная для пула соединений с БД
db_pool = None

# SQL-запрос для создания таблиц (если их нет)
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS reporters (
    id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    balance NUMERIC DEFAULT 0,
    PRIMARY KEY (id, chat_id)
);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    reporter_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    amount NUMERIC NOT NULL,
    recipient TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id, chat_id) REFERENCES reporters (id, chat_id) ON DELETE CASCADE
);
"""

# Функция для подключения к PostgreSQL и создания таблиц
async def create_db_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        user='ixlosfcu_taskManagerBot',       
        password='h2i-5wn-5Ah-Ufh',
        database='ixlosfcu_finhelp',
        host='localhost:5432'
    )
    async with db_pool.acquire() as connection:
        await connection.execute(CREATE_TABLES_SQL)  # Создание таблиц при старте
    logging.info("✅ Подключение к базе данных установлено. Таблицы проверены.")

# Функция инициализации
async def on_startup():
    await create_db_pool()

# Команда /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    welcome_text = (
        "👋 Привет! Я бот для учета финансовых расходов.\n\n"
        "📌 Доступные команды:\n"
        "🔹 /makereporter - назначить себя учетчиком расходов\n"
        "🔹 /add сумма - добавить текущий баланс (например, /add 100000)\n"
        "🔹 /take сумма - зафиксировать расход (например, /take 100000 - Иван)\n"
        "🔹 /report - получить отчет за текущий месяц\n\n"
        "💰 Все суммы указываются в долларах.\n"
        "🚀 Начнем!"
    )
    await message.answer(welcome_text)

# Команда /makereporter
@dp.message(Command("makereporter"))
async def makereporter_handler(message: types.Message):
    reporter_id = message.from_user.id
    chat_id = message.chat.id

    async with db_pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO reporters (id, chat_id, balance) 
            VALUES ($1, $2, 0) 
            ON CONFLICT (id, chat_id) DO NOTHING
            """,
            reporter_id, chat_id
        )
    await message.answer("✅ Вы назначены учетчиком расходов в этой группе.")

# Команда /add
@dp.message(Command("add"))
async def add_handler(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("⚠️ Укажите сумму после команды, например: /add 100000")
        return

    amount_text = re.sub(r"[^\d]", "", parts[1])
    try:
        amount = Decimal(amount_text)
    except ValueError:
        await message.answer("❌ Неправильный формат суммы.")
        return

    async with db_pool.acquire() as connection:
        result = await connection.fetchrow(
            "SELECT balance FROM reporters WHERE id = $1 AND chat_id = $2", user_id, chat_id
        )

        if result:
            current_balance = Decimal(result["balance"]) + amount
            await connection.execute(
                "UPDATE reporters SET balance = $1 WHERE id = $2 AND chat_id = $3",
                current_balance, user_id, chat_id
            )
        else:
            await connection.execute(
                """
                INSERT INTO reporters (id, chat_id, balance) 
                VALUES ($1, $2, $3) 
                ON CONFLICT (id, chat_id) DO UPDATE SET balance = EXCLUDED.balance
                """,
                user_id, chat_id, amount
            )
            current_balance = amount

    await message.answer(f"💰 Вы добавили ${amount}. Теперь у вас в кармане: ${current_balance}")

# Команда /take
@dp.message(Command("take"))
async def take_handler(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=2)

    if len(parts) < 2:
        await message.answer("⚠️ Укажите сумму расхода, например: /take 100000 - Иван")
        return

    pattern = r"(\d[\d\s\.]*)\s*(?:-?\s*(.+))?"
    match = re.match(pattern, " ".join(parts[1:]))
    if not match:
        await message.answer("❌ Неправильный формат команды. Используйте: /take сумма - получатель (опционально)")
        return

    amount_str, recipient = match.groups()
    amount_str = re.sub(r"[^\d]", "", amount_str)
    try:
        amount = Decimal(amount_str)
    except ValueError:
        await message.answer("❌ Ошибка в формате суммы.")
        return

    async with db_pool.acquire() as connection:
        result = await connection.fetchrow(
            "SELECT balance FROM reporters WHERE id = $1 AND chat_id = $2", user_id, chat_id
        )

        if not result:
            await message.answer("❌ Вы еще не добавили деньги. Используйте /add сначала.")
            return

        current_balance = Decimal(result["balance"])

        if amount > current_balance:
            await message.answer("❌ У вас недостаточно денег для этого расхода.")
            return

        new_balance = current_balance - amount

        await connection.execute(
            "UPDATE reporters SET balance = $1 WHERE id = $2 AND chat_id = $3",
            new_balance, user_id, chat_id
        )

        await connection.execute(
            "INSERT INTO expenses (reporter_id, chat_id, amount, recipient) VALUES ($1, $2, $3, $4)",
            user_id, chat_id, amount, recipient
        )

    response_text = f"✅ Вы потратили ${amount}. Осталось: ${new_balance}"
    if recipient:
        response_text += f" (на {recipient})"
    await message.answer(response_text)

# Основной запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await on_startup()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
