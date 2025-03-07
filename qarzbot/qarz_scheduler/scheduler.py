import asyncio
import logging
from aiogram import Bot, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from qarz_database.db_utils import get_db_pool
from qarz_config import API_TOKEN

# Enable logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize bot
bot = Bot(token=API_TOKEN)

# Dictionary to store pagination state for each user
user_pagination_state = {}

async def send_debt_reminders(interval_days: int):
    """Check for upcoming due debts and send reminders to users with an inline keyboard."""
    logger.info(f"\U0001F514 Checking for debts due in {interval_days} days...")

    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as db:
            # Fetch debts due in `interval_days` days for both debtors and borrowers
            query = """
            SELECT d.id, d.full_amount, d.currency, d.due_date, 
                   u.user_id as debtor_user_id, u.lang as debtor_lang,
                   u2.user_id as borrower_user_id, u2.lang as borrower_lang,
                   u2.fullname as borrower_name
            FROM debts d
            JOIN users u ON d.debtor_id = u.id
            JOIN users u2 ON d.borrower_id = u2.id
            WHERE EXISTS (
                SELECT 1 FROM jsonb_array_elements_text(d.due_date::jsonb) AS due
                WHERE TO_DATE(due::TEXT, 'DD.MM.YYYY') = CURRENT_DATE + INTERVAL '%s days'
            )
            AND d.status NOT IN ('completed', 'draft', 'overdue');
            """ % interval_days
            
            debts_due_soon = await db.fetch(query)

            if not debts_due_soon:
                logger.info(f"✅ No debts due in {interval_days} days.")
                return

            # Group debts by user
            user_debts = {}
            for debt in debts_due_soon:
                debtor_user_id = debt["debtor_user_id"]
                borrower_user_id = debt["borrower_user_id"]
                debtor_lang = debt["debtor_lang"]
                borrower_lang = debt["borrower_lang"]

                if debtor_user_id not in user_debts:
                    user_debts[debtor_user_id] = {"lang": debtor_lang, "debts": []}
                if borrower_user_id not in user_debts:
                    user_debts[borrower_user_id] = {"lang": borrower_lang, "debts": []}

                user_debts[debtor_user_id]["debts"].append(debt)
                user_debts[borrower_user_id]["debts"].append(debt)

            # Send reminders to each user
            for user_id, data in user_debts.items():
                lang = data["lang"]
                debts = data["debts"]

                # Prepare the message based on the user's role (debtor or borrower)
                messages = {
                    "ru": {
                        "debtor": f"⏳ У вас есть долги с предстоящими сроками погашения через {interval_days} дней. Мы также отправили напоминание заемщику. Пожалуйста, проверьте их ниже:",
                        "borrower": f"⏳ У вас есть долги для оплаты с предстоящими сроками погашения через {interval_days} дней. Пожалуйста, проверьте их ниже:"
                    },
                    "uz": {
                        "debtor": f"⏳ Sizda {interval_days} kun ichida to'lanishi kerak bo'lgan qarzlaringiz bor. Biz ham qarz oluvchiga eslatma yubordik. Iltimos, ularni quyida ko'rib chiqing:",
                        "borrower": f"⏳ Sizda {interval_days} kun ichida to'lanishi kerak bo'lgan qarzlaringiz bor. Iltimos, ularni quyida ko'rib chiqing:"
                    },
                    "oz": {
                        "debtor": f"⏳ Сизда {interval_days} кун ичида тўланиши керак бўлган қарзларингиз бор. Биз ҳам қарз олувчига эслатма юбордик. Илтимос, уларни қуйида кўриб чикинг:",
                        "borrower": f"⏳ Сизда {interval_days} кун ичида тўланиши керак бўлган қарзларингиз бор. Илтимос, уларни қуйида кўриб чикинг:"
                    }
                }

                # Determine if the user is a debtor or borrower
                role = "debtor" if any(debt["debtor_user_id"] == user_id for debt in debts) else "borrower"
                message = messages.get(lang, messages["uz"])[role]  # Default to Uzbek

                # Pagination logic
                page = user_pagination_state.get(user_id, 0)  # Get current page for the user
                start = page * 10
                end = start + 10
                paginated_debts = debts[start:end]

                # Create a list to hold multiple buttons (one button per row)
                debt_buttons = []
                for debt in paginated_debts:
                    amount = debt["full_amount"]
                    currency = debt["currency"]
                    debt_id = debt["id"]
                    borrower_name = debt["borrower_name"]
                    
                    debt_buttons.append([types.InlineKeyboardButton(
                        text=f"Долг: {borrower_name} - {amount} {currency}",
                        callback_data=f"debt_{debt_id}"
                    )])

                # Add pagination buttons if needed
                pagination_buttons = []
                if page > 0:
                    pagination_buttons.append(types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data=f"prev_page_{user_id}"
                    ))
                if end < len(debts):
                    pagination_buttons.append(types.InlineKeyboardButton(
                        text="Вперёд ➡️", callback_data=f"next_page_{user_id}"
                    ))

                if pagination_buttons:
                    debt_buttons.append(pagination_buttons)

                # Create the inline keyboard
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=debt_buttons)

                # Send the message with inline keyboard
                await bot.send_message(user_id, message, reply_markup=keyboard)
                logger.info(f"📩 Reminder with debts list sent to User ID {user_id}.")

    except Exception as e:
        logger.error(f"❌ Error in send_debt_reminders: {e}")

async def check_overdue_debts():
    """Check for overdue debts and update their status to 'overdue'."""
    logger.info("\U0001F514 Checking for overdue debts...")

    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as db:
            # Fetch debts that are past their due date and not fully paid
            query = """
            UPDATE debts
            SET status = 'overdue'
            WHERE EXISTS (
                SELECT 1 FROM jsonb_array_elements_text(due_date::jsonb) AS due
                WHERE TO_DATE(due::TEXT, 'DD.MM.YYYY') < CURRENT_DATE
            )
            AND status NOT IN ('completed', 'overdue')
            RETURNING id;
            """
            
            updated_debts = await db.fetch(query)

            if updated_debts:
                logger.info(f"✅ Updated {len(updated_debts)} debts to 'overdue'.")
            else:
                logger.info("✅ No overdue debts found.")

    except Exception as e:
        logger.error(f"❌ Error in check_overdue_debts: {e}")

# Initialize the scheduler
scheduler = AsyncIOScheduler()

hour = 22
minute = 8

# Schedule reminders for 7, 3, and 1 day before the due date
scheduler.add_job(send_debt_reminders, "cron", hour=hour, minute=minute, args=[7])  # 7 days before
scheduler.add_job(send_debt_reminders, "cron", hour=hour, minute=minute, args=[2])  # 3 days before
scheduler.add_job(send_debt_reminders, "cron", hour=hour, minute=minute, args=[1])  # 1 day before

# Schedule overdue debt check daily
scheduler.add_job(check_overdue_debts, "cron", hour=hour, minute=minute)  # Check overdue debts daily