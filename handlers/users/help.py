from aiogram import types
from aiogram.types import InputFile

from loader import dp, bot

from inline_keyboards.circuit_race_keyboards import RaceInlineKeyboard


@dp.message_handler(text="/help")
async def command_start(message: types.Message):
    h_menu, menu = RaceInlineKeyboard.get_event_menu([1, 4, 7])
    photo = InputFile('images/races/events/uncontrollable_skid.jpg')

    await bot.send_photo(message.chat.id, photo, reply_markup=menu)
