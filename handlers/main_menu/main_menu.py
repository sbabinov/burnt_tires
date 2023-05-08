import os.path

from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, InputMedia

from loader import dp, bot, update_current_message_id, check_current_message_id
from states import MainState

from aiogram.dispatcher.filters import Command
from aiogram import types

from inline_keyboards import InlineKeyboard


# главное меню
@dp.message_handler(Command('menu'))
async def main_menu(message: types.Message):
    user_id = message.from_user.id

    image = InputFile(os.path.join('images/design/main_menu.jpg'))

    chat_id = message.chat.id
    message = await bot.send_photo(chat_id, photo=image, reply_markup=InlineKeyboard.main_menu)

    update_current_message_id(user_id, message.message_id)


@dp.callback_query_handler(text='главное меню')
async def main_menu_call(call: types.CallbackQuery):
    if await check_current_message_id(call):
        image = InputFile(os.path.join('images/design/main_menu.jpg'))
        media = InputMedia(media=image)

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        message = await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                               reply_markup=InlineKeyboard.main_menu)
