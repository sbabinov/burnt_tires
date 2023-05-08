import os.path

from aiogram.types import InputFile, CallbackQuery, InputMedia

from loader import dp, bot, check_current_message_id, update_service_data, get_service_data
from inline_keyboards import InlineKeyboard
from useful_function.generate_car_pictures import *


# тюнинг меню
@dp.callback_query_handler(text_contains='гар-тюнинг')
async def tuning_menu(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id
        car_id = get_service_data(user_id, 'car_id')

        update_service_data(user_id, 'choose_detail_index', 0)

        data = cursor.execute("SELECT * FROM users_cars WHERE (user_id, car_id) = (?, ?)", (user_id, car_id)).fetchone()
        improvements = data[2:-1]

        shop_image_path = generate_autoparts_shop(user_id, improvements, choose_detail_index=0)
        shop_image = InputMedia(media=InputFile(shop_image_path))

        inline_keyboard = InlineKeyboard.get_autoshop_menu()

        await bot.edit_message_media(media=shop_image, message_id=call.message.message_id, chat_id=call.message.chat.id,
                                     reply_markup=inline_keyboard)
        os.remove(shop_image_path)


@dp.callback_query_handler(text_contains='тюн_')
async def tuning_menu_move(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id

        direction = call.data.split('_')[1]

        car_id = get_service_data(user_id, 'car_id')
        show_prices = get_service_data(user_id, 'show_prices')
        choose_detail_index = get_service_data(user_id, 'choose_detail_index')

        fast_load = True

        if direction == 'назад':
            fast_load = False
        elif direction == 'вправо':
            choose_detail_index += 1
            if choose_detail_index > 11:
                choose_detail_index = 0
        elif direction == 'влево':
            choose_detail_index -= 1
            if choose_detail_index < 0:
                choose_detail_index = 11
        elif direction == 'вниз':
            if choose_detail_index > 7:
                choose_detail_index -= 8
            else:
                choose_detail_index += 4
        elif direction == 'вверх':
            if choose_detail_index < 4:
                choose_detail_index += 8
            else:
                choose_detail_index -= 4

        update_service_data(user_id, 'choose_detail_index', choose_detail_index)

        data = cursor.execute("SELECT * FROM users_cars WHERE (user_id, car_id) = (?, ?)", (user_id, car_id)).fetchone()
        improvements = data[2:-1]

        menu_image_path = generate_autoparts_shop(user_id, improvements, choose_detail_index, show_prices=show_prices,
                                                  fast_load=fast_load)
        menu_image = InputMedia(media=InputFile(menu_image_path))

        inline_menu = InlineKeyboard.get_autoshop_menu(show_prices=show_prices)

        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=menu_image,
                                     reply_markup=inline_menu)
        os.remove(menu_image_path)


@dp.callback_query_handler(text_contains='тюн-цены_')
async def tuning_menu_prices(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id
        choose_detail_index = get_service_data(user_id, 'choose_detail_index')
        car_id = get_service_data(user_id, 'car_id')

        show_prices = get_service_data(user_id, 'show_prices')
        show_prices = 0 if show_prices == 1 else 1
        update_service_data(user_id, 'show_prices', show_prices)

        data = cursor.execute("SELECT * FROM users_cars WHERE (user_id, car_id) = (?, ?)", (user_id, car_id)).fetchone()
        improvements = data[2:-1]

        menu_image_path = generate_autoparts_shop(user_id, improvements, choose_detail_index, show_prices=show_prices)
        menu_image = InputMedia(media=InputFile(menu_image_path))

        inline_menu = InlineKeyboard.get_autoshop_menu(show_prices=show_prices)

        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=menu_image,
                                     reply_markup=inline_menu)
        os.remove(menu_image_path)


@dp.callback_query_handler(text_contains='тюн-выбрать_')
async def tuning_choose_detail(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id

        choose_detail_index = get_service_data(user_id, 'choose_detail_index')
        car_id = get_service_data(user_id, 'car_id')

        update_service_data(user_id, 'car_part_index', choose_detail_index)

        car_part = car_parts_list[choose_detail_index]
        car_part_status = cursor.execute(f"SELECT {car_part} FROM users_cars WHERE (user_id, car_id) = (?, ?)",
                                         (user_id, car_id)).fetchone()[0]

        image_path = generate_car_part_image(user_id, choose_detail_index, car_id, car_part_status=car_part_status)
        menu_image = InputMedia(media=InputFile(image_path))

        inline_menu = InlineKeyboard.get_car_part_menu(car_part_status)

        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=menu_image,
                                     reply_markup=inline_menu)
        os.remove(image_path)


@dp.callback_query_handler(text='установить-деталь')
async def set_detail(call: CallbackQuery):
    if await check_current_message_id(call, show_alert=False):
        user_id = call.from_user.id

        car_id = get_service_data(user_id, 'car_id')
        car_part_index = get_service_data(user_id, 'car_part_index')

        car_part = car_parts_list[car_part_index]
        car_part_status = cursor.execute(f"SELECT {car_part} FROM users_cars WHERE (user_id, car_id) = (?, ?)",
                                         (user_id, car_id)).fetchone()[0]

        if car_part_status == 0:
            user_balance = cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,)).fetchone()[0]
            user_car_parts_amount = \
                cursor.execute(f"SELECT {car_part} FROM user_car_parts_amount WHERE user_id = ?",
                               (user_id,)).fetchone()[0]

            car_part_price = car_parts_prices_and_amounts[car_part][0]
            car_part_amount = car_parts_prices_and_amounts[car_part][1]

            if user_balance < car_part_price:
                await call.answer("❌ У вас недостаточно средств для покупки улучшения!", show_alert=True)
            elif user_car_parts_amount < car_part_amount:
                await call.answer("❌ У вас недостаточно карточек для покупки улучшения!", show_alert=True)
            else:
                car_part_title = car_parts_short[car_part]
                new_balance = user_balance - car_part_price
                new_car_parts_amount = user_car_parts_amount - car_part_amount

                cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
                cursor.execute(f"UPDATE user_car_parts_amount SET {car_part} = ? WHERE id = ?",
                               (new_car_parts_amount, user_id))
                connection.commit()

                car_part_status = 1

                await call.answer(f"✅ Поздравляем! Вы успешно купили {car_part_title}", show_alert=True)
        elif car_part_status == 1:
            car_part_status = 2
        else:
            car_part_status = 1

        cursor.execute(f"UPDATE users_cars SET {car_part} = ? WHERE car_id = ?", (car_part_status, car_id))
        connection.commit()

        image_path = generate_car_part_image(user_id, car_part_index, car_id, car_part_status=car_part_status)
        menu_image = InputMedia(media=InputFile(image_path))

        inline_menu = InlineKeyboard.get_car_part_menu(car_part_status)

        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=menu_image,
                                     reply_markup=inline_menu)
        os.remove(image_path)




