from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import CallbackQuery

import sqlite3

from data import config

# бот
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# бд
connection = sqlite3.connect('server.db')
cursor = connection.cursor()

# машина состояний
storage = MemoryStorage()

# диспетчер
dp = Dispatcher(bot, storage=storage)


# функция для обновления текущего ID сообщения
def update_current_message_id(user_id: int, message_id: int):
    current_user_message = \
        cursor.execute("SELECT message_id FROM current_user_message WHERE user_id = ?", (user_id,)).fetchone()
    if not current_user_message:
        cursor.execute("INSERT INTO current_user_message VALUES (?, ?)", (user_id, message_id))
        connection.commit()
    else:
        cursor.execute("UPDATE current_user_message SET message_id = ? WHERE user_id = ?", (message_id, user_id))
        connection.commit()


# функция для проверки ID текущего сообщения
async def check_current_message_id(call: CallbackQuery, show_alert=True):
    user_id = call.from_user.id
    message_id = call.message.message_id

    current_message_id = \
        cursor.execute("SELECT message_id FROM current_user_message WHERE user_id = ?", (user_id,)).fetchone()[0]

    if current_message_id != message_id:
        await call.answer("❌ Данное меню устарело!", show_alert=True)
        return False

    if show_alert:
        await call.answer()
    return True


# функция для занесения служебных данных в БД
def update_service_data(user_id: int, name: str, value: any):
    cursor.execute(f"UPDATE service_data SET '{name}' = ? WHERE user_id = ?", (value, user_id))
    connection.commit()


# функция для прочтения служебных данных из БД
def get_service_data(user_id: int, name: str):
    value = cursor.execute(f"SELECT {name} FROM service_data WHERE user_id = ?", (user_id,)).fetchone()[0]
    return value
