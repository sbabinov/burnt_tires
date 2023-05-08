import asyncio
import os

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, cursor, connection
from states import Registration, MainState


def insert_to_db_on_start(user_id: int, username: str):
    cursor.execute("INSERT INTO service_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    cursor.execute(f"INSERT INTO user_car_parts_amount VALUES (?{', ?' * 12})",
                   (user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    cursor.execute(f"INSERT INTO user_car_parts_amount VALUES (?{', ?' * 12})",
                   (user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user_id, username, 0, ''))
    connection.commit()

    connection.commit()


@dp.message_handler(text="/start")
async def command_start(message: types.Message):
    user_id = message.from_user.id

    if_exists = bool(cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone())
    if if_exists:
        cursor.execute("INSERT INTO service_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (user_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        await message.answer("❗️ Вы уже зарегистрированы!")
    else:
        await Registration.username.set()
        await message.answer("Добро пожаловать! Введите юзернейм, который хотите использовать:")


@dp.message_handler(state=Registration.username)
async def get_username(message: types.Message, state: FSMContext):
    username = message.text
    user_id = message.from_user.id

    insert_to_db_on_start(user_id, username)

    os.mkdir(os.path.join(f'images/for_saves/{user_id}'))

    await state.finish()
    await message.answer("Поздравляем! Вы успешно зарегистрировались!")
    await MainState.main_state.set()


@dp.message_handler(text="/car")
async def get_car(message: types.Message):
    user_id = message.from_user.id

    car_id = 1
    cursor.execute(f"INSERT INTO users_cars VALUES (?{', ?' * 14})", (user_id, car_id, 0,0,0,0,0,0,0,0,0,0,0,0,''))
    connection.commit()
    print('ok')


