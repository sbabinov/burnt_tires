import os.path

from aiogram.types import InputFile, CallbackQuery, InputMedia

from loader import dp, bot, check_current_message_id, update_service_data, get_service_data
from inline_keyboards import InlineKeyboard
from useful_function.generate_car_pictures import *


# тюнинг меню
@dp.callback_query_handler(text_contains='гар-шины')
async def tires_menu(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id

        car_id = get_service_data(user_id, 'car_id')
        choose_tires_index = get_service_data(user_id, 'choose_tires_index')

        image_path = generate_tires_menu_picture(user_id, car_id, choose_tires_index)
        image = InputMedia(media=InputFile(image_path))

        inline_keyboard = InlineKeyboard.tires_menu

        await bot.edit_message_media(media=image, message_id=call.message.message_id, chat_id=call.message.chat.id,
                                     reply_markup=inline_keyboard)
        os.remove(image_path)


@dp.callback_query_handler(text_contains='шин_')
async def tires_menu_move(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id

        direction = call.data.split('_')[1]

        car_id = get_service_data(user_id, 'car_id')
        choose_tires_index = get_service_data(user_id, 'choose_tires_index')

        if direction == 'назад':
            ...
        elif direction == 'вправо':
            choose_tires_index += 1
            if choose_tires_index >= 7:
                choose_tires_index = 0
        elif direction == 'влево':
            choose_tires_index -= 1
            if choose_tires_index < 0:
                choose_tires_index = 6

        update_service_data(user_id, 'choose_tires_index', choose_tires_index)

        image_path = generate_tires_menu_picture(user_id, car_id, choose_tires_index)
        image = InputMedia(media=InputFile(image_path))

        inline_keyboard = InlineKeyboard.tires_menu

        await bot.edit_message_media(media=image, message_id=call.message.message_id, chat_id=call.message.chat.id,
                                     reply_markup=inline_keyboard)
        os.remove(image_path)


@dp.callback_query_handler(text='шин-выбрать_')
async def tires_menu(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id

        car_id = get_service_data(user_id, 'car_id')
        choose_tires_index = get_service_data(user_id, 'choose_tires_index')

        image_path = generate_tires_management_menu_picture(user_id, car_id, choose_tires_index)
        image = InputMedia(media=InputFile(image_path))

        inline_keyboard = InlineKeyboard.tires_managment_menu

        await bot.edit_message_media(media=image, message_id=call.message.message_id, chat_id=call.message.chat.id,
                                     reply_markup=inline_keyboard)
        os.remove(image_path)



