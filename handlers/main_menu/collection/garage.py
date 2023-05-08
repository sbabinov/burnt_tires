import os.path

from aiogram.types import InputFile, CallbackQuery, InputMedia

from loader import dp, bot, check_current_message_id, update_service_data, get_service_data
from inline_keyboards import InlineKeyboard
from useful_function.generate_car_pictures import *


@dp.callback_query_handler(text='в гараж_')
async def to_garage(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id

        car_id = get_service_data(user_id, 'car_id')
        garage_image_path = generate_garage_picture(user_id, car_id)

        media = InputMedia(media=InputFile(garage_image_path))

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                     reply_markup=InlineKeyboard.garage_menu)


@dp.callback_query_handler(text='показать меню_')
async def show_car(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id

        car_id = get_service_data(user_id, 'car_id')
        garage_image_path = generate_garage_picture(user_id, car_id, show_menu=True)

        update_service_data(user_id, 'garage_menu_index', 0)
        update_service_data(user_id, 'choose_tires_index', 0)

        media = InputMedia(media=InputFile(garage_image_path))

        garage_menu = InlineKeyboard.get_garage_menu_2()

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                     reply_markup=garage_menu)
        os.remove(garage_image_path)


@dp.callback_query_handler(text_contains='гар_')
async def garage_menu_move(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id
        direction = call.data.split('_')[1]

        garage_menu_index = get_service_data(user_id, 'garage_menu_index')
        if direction == 'вправо':
            garage_menu_index += 1
            if garage_menu_index > 3:
                garage_menu_index = 0
        elif direction == 'влево':
            garage_menu_index -= 1
            if garage_menu_index < 0:
                garage_menu_index = 3

        update_service_data(user_id, 'garage_menu_index', garage_menu_index)

        car_id = get_service_data(user_id, 'car_id')
        garage_image_path = generate_garage_picture(user_id, car_id, show_menu=True, menu_index=garage_menu_index)

        media = InputMedia(media=InputFile(garage_image_path))

        garage_menu = InlineKeyboard.get_garage_menu_2(garage_menu_index)

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                     reply_markup=garage_menu)
        os.remove(garage_image_path)

