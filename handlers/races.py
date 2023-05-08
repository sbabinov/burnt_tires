import os
import asyncio

from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, bot
from aiogram.dispatcher.filters import Command
from aiogram import types
# from generate_garage_picture import generate_car_photo, generate_car_characteristics_photo

from inline_keyboards import InlineKeyboard


# главное меню
@dp.message_handler(Command('r1'))
async def main_menu(message: types.Message):
    image = InputFile('images/race_circuits/monza/start.jpg')

    races = InlineKeyboardMarkup(row_width=1,
                                 inline_keyboard=[
                                         [
                                             InlineKeyboardButton(text='🚗 Старт!', callback_data='курсы'),
                                         ],
                                     ],
                                 )

    frames = [
        '<i>🚦 Приготовьтесь...</i>\n\n'
        '⚪️ ⚪️ ⚪️ ⚪️ ⚪️\n'
        '⚪️ ⚪️ ⚪️ ⚪️ ⚪️',
        '<i>🚦 Приготовьтесь...</i>\n\n'
        '🔴 ⚪️ ⚪️ ⚪️ ⚪️\n'
        '🔴 ⚪️ ⚪️ ⚪️ ⚪️',
        '<i>🚦 Приготовьтесь...</i>\n\n'
        '🔴 🔴 ⚪️ ⚪️ ⚪️\n'
        '🔴 🔴 ⚪️ ⚪️ ⚪️',
        '<i>🚦 Приготовьтесь...</i>\n\n'
        '🔴 🔴 🔴 ⚪️ ⚪️\n'
        '🔴 🔴 🔴 ⚪️ ⚪️',
        '<i>🚦 Приготовьтесь...</i>\n\n'
        '🔴 🔴 🔴 🔴 ⚪️\n'
        '🔴 🔴 🔴 🔴 ⚪️',
        '<i>🚦 Приготовьтесь...</i>\n\n'
        '🔴 🔴 🔴 🔴 🔴\n'
        '🔴 🔴 🔴 🔴 🔴',
        '<i>🚦 СТАРТ!</i>\n\n'
        '⚪️ ⚪️ ⚪️ ⚪️ ⚪️\n'
        '⚪️ ⚪️ ⚪️ ⚪️ ⚪️'
    ]

    msg = await message.answer(frames[0])

    chat_id = message.chat.id
    await bot.send_photo(chat_id=chat_id, photo=image, reply_markup=races)
    for i in range(1, len(frames)):
        await asyncio.sleep(1.5)
        await msg.edit_text(frames[i])