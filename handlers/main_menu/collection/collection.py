import os.path

from aiogram.types import InputFile, CallbackQuery, InputMedia

from loader import dp, bot, check_current_message_id, update_service_data, get_service_data
from inline_keyboards import InlineKeyboard
from useful_function.generate_car_pictures import *


def sort_brands_by_alphabet(brands: list):
    sorted_brands = sorted(brands, key=lambda x: cars_brands[x])
    # sorted_brands = [1, 2, 3, 2, 3, 1, 2, 1, 3, 1, 3, 2, 1, 2, 3]
    brands_groups = [[]]
    for brand_id in sorted_brands:
        if len(brands_groups[-1]) < 6:
            brands_groups[-1].append(brand_id)
        else:
            brands_groups.append([brand_id])
    return brands_groups


def get_car_groups(brand_id: int):
    brand_cars_ids = [i[0] for i in cursor.execute("SELECT id FROM cars WHERE car_brand = ?",
                                                   (brand_id,)).fetchall()]
    cars_groups = [[]]
    for car_id in brand_cars_ids:
        if len(cars_groups[-1]) < 9:
            cars_groups[-1].append(car_id)
        else:
            cars_groups.append([car_id])

    return cars_groups


# выбор коллекции
@dp.callback_query_handler(text='коллекция')
async def choose_collection(call: CallbackQuery):
    if await check_current_message_id(call):
        image = InputFile(os.path.join('images/design/choose_collection.jpg'))
        media = InputMedia(media=image)

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                     reply_markup=InlineKeyboard.choose_collection)


# коллекция автомобилей
@dp.callback_query_handler(text='авто')
async def car_collection(call: CallbackQuery):
    if await check_current_message_id(call):
        brands_groups = sort_brands_by_alphabet(cars_brands)

        menu_image_path = generate_car_collection_menu_image(brands_groups[0], 0)
        menu_image = InputMedia(media=InputFile(menu_image_path))

        inline_menu = InlineKeyboard.get_car_brands_menu(0, 0)

        update_service_data(call.from_user.id, 'brand_page_index', 0)
        update_service_data(call.from_user.id, 'choose_brand_index', 0)

        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=menu_image,
                                     reply_markup=inline_menu)
        os.remove(menu_image_path)


@dp.callback_query_handler(text_contains='авт_')
async def car_collection_move(call: CallbackQuery):
    user_id = call.from_user.id
    if await check_current_message_id(call):
        direction = call.data.split('_')[1]

        page_index = get_service_data(user_id, 'brand_page_index')
        if direction != 'след' and direction != 'пред':
            choose_brand_index = get_service_data(user_id, 'choose_brand_index')
        else:
            choose_brand_index = 0
        brands_groups = sort_brands_by_alphabet(cars_brands)

        if direction == 'назад':
            ...
        elif direction == 'вправо':
            choose_brand_index += 1
            if choose_brand_index >= len(brands_groups[page_index]):
                choose_brand_index = 0
        elif direction == 'влево':
            choose_brand_index -= 1
            if choose_brand_index < 0:
                choose_brand_index = len(brands_groups[page_index]) - 1
        elif direction == 'вниз':
            if choose_brand_index > 2:
                choose_brand_index -= 3
            else:
                choose_brand_index += 3
                try:
                    brands_groups[page_index][choose_brand_index]
                except IndexError:
                    choose_brand_index = len(brands_groups[page_index]) - 1
        elif direction == 'вверх':
            if choose_brand_index < 3:
                choose_brand_index += 3
                try:
                    brands_groups[page_index][choose_brand_index]
                except IndexError:
                    choose_brand_index = len(brands_groups[page_index]) - 1
            else:
                choose_brand_index -= 3
        elif direction == 'след':
            choose_brand_index = 0
            page_index += 1
            if page_index >= len(brands_groups):
                page_index = 0
        elif direction == 'пред':
            choose_brand_index = 0
            page_index -= 1
            if page_index == -1:
                page_index = len(brands_groups) - 1

        update_service_data(user_id, 'brand_page_index', page_index)
        update_service_data(user_id, 'choose_brand_index', choose_brand_index)

        menu_image_path = generate_car_collection_menu_image(brands_groups[page_index], choose_brand_index)
        menu_image = InputMedia(media=InputFile(menu_image_path))

        inline_menu = InlineKeyboard.get_car_brands_menu(page_index, choose_brand_index)

        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=menu_image,
                                     reply_markup=inline_menu)
        os.remove(menu_image_path)


# первая страница коллекции
@dp.callback_query_handler(text_contains='выбрать-бренд_')
async def show_collection_first_page(call: CallbackQuery):
    user_id = call.from_user.id
    if await check_current_message_id(call):
        page_index = get_service_data(user_id, 'brand_page_index')
        choose_brand_index = get_service_data(user_id, 'choose_brand_index')

        brands_groups = sort_brands_by_alphabet(cars_brands)
        choose_brand_id = brands_groups[page_index][choose_brand_index]

        update_service_data(user_id, 'choose_brand_id', choose_brand_id)

        brand_cars_ids = [i[0] for i in cursor.execute("SELECT id FROM cars WHERE car_brand = ?",
                                                       (choose_brand_id,)).fetchall()]
        cars_groups = [[]]
        for car_id in brand_cars_ids:
            if len(cars_groups[-1]) < 9:
                cars_groups[-1].append(car_id)
            else:
                cars_groups.append([car_id])

        brand_album_image_path = generate_brand_image(choose_brand_id)
        media = InputMedia(media=InputFile(brand_album_image_path))

        inline_keyboard = InlineKeyboard.get_car_collection_first_page(choose_brand_id)

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id, reply_markup=inline_keyboard)
        os.remove(brand_album_image_path)


@dp.callback_query_handler(text_contains='к коллекции_')
async def to_car_collection(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id
        brand_id = get_service_data(user_id, 'choose_brand_id')

        cars_groups = get_car_groups(brand_id)

        # for file in os.listdir(os.path.join(f'images/for_saves/{user_id}')):
        #     os.remove(os.path.join(f'images/for_saves/{user_id}/{file}'))

        album_photo_path = generate_album_photo(user_id, brand_id, cars_groups[0], 0)
        media = InputMedia(media=InputFile(album_photo_path))

        update_service_data(user_id, 'car_page_index', 0)
        update_service_data(user_id, 'choose_car_index', 0)
        update_service_data(user_id, 'brand_id', brand_id)

        inline_keyboard = InlineKeyboard.get_car_collection_menu(user_id)

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id, reply_markup=inline_keyboard)
        os.remove(album_photo_path)


@dp.callback_query_handler(text_contains='кол_')
async def car_collection_move(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id
        direction = call.data.split('_')[1]
        page_index = get_service_data(user_id, 'car_page_index')
        brand_id = get_service_data(user_id, 'brand_id')

        cars_groups = get_car_groups(brand_id)

        if direction != 'след' and direction != 'пред':
            choose_car_index = get_service_data(user_id, 'choose_car_index')
        else:
            choose_car_index = 0

        if direction == 'назад':
            ...
            # for file in os.listdir(os.path.join(f'images/for_saves/{user_id}')):
            #     os.remove(os.path.join(f'images/for_saves/{user_id}/{file}'))
        elif direction == 'вправо':
            choose_car_index += 1
            if choose_car_index >= len(cars_groups[page_index]):
                choose_car_index = 0
        elif direction == 'влево':
            choose_car_index -= 1
            if choose_car_index < 0:
                choose_car_index = len(cars_groups[page_index]) - 1
        elif direction == 'вниз':
            if choose_car_index > 2:
                choose_car_index -= 3
            else:
                choose_car_index += 3
                try:
                    cars_groups[page_index][choose_car_index]
                except IndexError:
                    choose_car_index = len(cars_groups[page_index]) - 1
        elif direction == 'вверх':
            if choose_car_index < 3:
                choose_car_index += 3
                try:
                    cars_groups[page_index][choose_car_index]
                except IndexError:
                    choose_car_index = len(cars_groups[page_index]) - 1
            else:
                choose_car_index -= 3
        elif direction == 'след':
            choose_car_index = 0
            page_index += 1
            if page_index >= len(cars_groups):
                page_index = 0
        elif direction == 'пред':
            choose_car_index = 0
            page_index -= 1
            if page_index == -1:
                page_index = len(cars_groups) - 1

        update_service_data(user_id, 'car_page_index', page_index)
        update_service_data(user_id, 'choose_car_index', choose_car_index)

        menu_image_path = generate_album_photo(user_id, brand_id, cars_groups[page_index], choose_car_index,
                                               fast_load=True)
        menu_image = InputMedia(media=InputFile(menu_image_path))

        inline_menu = InlineKeyboard.get_car_collection_menu(user_id)

        await bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=menu_image,
                                     reply_markup=inline_menu)
        os.remove(menu_image_path)


@dp.callback_query_handler(text_contains='выбрать авто')
async def choose_car_from_collection(call: CallbackQuery):
    if await check_current_message_id(call, show_alert=False):
        user_id = call.from_user.id

        page_index = get_service_data(user_id, 'car_page_index')
        brand_id = get_service_data(user_id, 'brand_id')
        choose_car_index = get_service_data(user_id, 'choose_car_index')

        cars_groups = get_car_groups(brand_id)

        car_id = cars_groups[page_index][choose_car_index]

        update_service_data(user_id, 'car_id', car_id)

        opened_car_ids = \
            [i[0] for i in cursor.execute("SELECT car_id FROM users_cars WHERE user_id = ?", (user_id,)).fetchall()]
        if car_id not in opened_car_ids:
            await call.answer('🔒 У вас еще не открыт этот автомобиль!', show_alert=True)
        else:
            card_picture_path = generate_card_picture(user_id, car_id)

            media = InputMedia(media=InputFile(card_picture_path))

            inline_keyboard = InlineKeyboard.get_card_picture_menu('back')

            chat_id = call.message.chat.id
            message_id = call.message.message_id

            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=inline_keyboard)
            os.remove(card_picture_path)


@dp.callback_query_handler(text_contains='повернуть карточку_')
async def show_card_backside(call: CallbackQuery):
    if await check_current_message_id(call):
        user_id = call.from_user.id

        car_id = get_service_data(user_id, 'car_id')
        side = call.data.split('_')[1]

        card_picture_path = generate_card_picture(car_id, backside=True if side == 'back' else False)
        media = InputMedia(media=InputFile(card_picture_path))

        if side == 'back':
            side = 'front'
        else:
            side = 'back'

        inline_keyboard = InlineKeyboard.get_card_picture_menu(side)

        chat_id = call.message.chat.id
        message_id = call.message.message_id

        await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                     reply_markup=inline_keyboard)
        os.remove(card_picture_path)


