from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import cursor, get_service_data


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


class InlineKeyboard:
    # главное меню
    main_menu = InlineKeyboardMarkup(row_width=1,
                                     inline_keyboard=[
                                         [
                                             InlineKeyboardButton(text='🎲 Играть', callback_data='курсы'),
                                             InlineKeyboardButton(text='👤 Профиль', callback_data='задачи')
                                         ],
                                         [
                                             InlineKeyboardButton(text='📒 Коллекция', callback_data='коллекция'),
                                             InlineKeyboardButton(text='⚙️ Настройки', callback_data='настройки')
                                         ],
                                     ],
                                     )

    # выбор коллекции
    choose_collection = InlineKeyboardMarkup(row_width=1,
                                             inline_keyboard=[
                                                 [
                                                     InlineKeyboardButton(text='🚗 Авто', callback_data='авто'),
                                                     InlineKeyboardButton(text='🏁 Трассы', callback_data='трассы'),

                                                 ],
                                                 [
                                                     InlineKeyboardButton(text='↩️ Назад', callback_data='главное меню')
                                                 ],
                                             ],
                                             )

    # меню коллекции автомобилей
    @staticmethod
    def get_car_brands_menu(page_index, choose_brand_index):
        first_row = [
            InlineKeyboardButton(text='⬅️', callback_data=f'авт_влево_{page_index}_{choose_brand_index}'),
            InlineKeyboardButton(text='➡️', callback_data=f'авт_вправо_{page_index}_{choose_brand_index}'),
            InlineKeyboardButton(text='⬆️', callback_data=f'авт_вверх_{page_index}_{choose_brand_index}'),
            InlineKeyboardButton(text='⬇️', callback_data=f'авт_вниз_{page_index}_{choose_brand_index}')
        ]
        second_row = [
            InlineKeyboardButton(text='⏪', callback_data=f'авт_пред_{page_index}'),
            InlineKeyboardButton(text='✅ Выбрать', callback_data=f'выбрать-бренд_{page_index}_{choose_brand_index}'),
            InlineKeyboardButton(text='⏩', callback_data=f'авт_след_{page_index}')
        ]

        car_collection_menu = \
            InlineKeyboardMarkup(row_width=1,
                                 inline_keyboard=[
                                     first_row,
                                     second_row,
                                     [
                                         InlineKeyboardButton(text='↩️ Назад', callback_data='коллекция')
                                     ],
                                 ],
                                 )
        return car_collection_menu

    # меню для первой страницы коллекции автомобилей
    @staticmethod
    def get_car_collection_first_page(brand_id):
        car_collection_first_page = \
            InlineKeyboardMarkup(row_width=1,
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='✅ К коллекции',
                                                              callback_data=f'к коллекции_{brand_id}'),

                                     ],
                                     [
                                         InlineKeyboardButton(text='↩️ Назад', callback_data=
                                         f'авт_назад')
                                     ],
                                 ],
                                 )
        return car_collection_first_page

    # меню для остальных страниц коллекции автомобилей
    @staticmethod
    def get_car_collection_menu(user_id):
        opened_car_ids = \
            [i[0] for i in cursor.execute("SELECT car_id FROM users_cars WHERE user_id = ?", (user_id,)).fetchall()]
        page_index = get_service_data(user_id, 'car_page_index')
        brand_id = get_service_data(user_id, 'brand_id')
        choose_car_index = get_service_data(user_id, 'choose_car_index')

        car_groups = get_car_groups(brand_id)
        if car_groups[page_index][choose_car_index] not in opened_car_ids:
            caption = '🔒 Закрыто'
        else:
            caption = '✅ Выбрать'

        first_row = [
            InlineKeyboardButton(text='⬅️', callback_data=f'кол_влево'),
            InlineKeyboardButton(text='➡️', callback_data=f'кол_вправо'),
            InlineKeyboardButton(text='⬆️', callback_data=f'кол_вверх'),
            InlineKeyboardButton(text='⬇️', callback_data=f'кол_вниз')
        ]
        second_row = [
            InlineKeyboardButton(text='⏪', callback_data=f'кол_пред'),
            InlineKeyboardButton(text=caption,
                                 callback_data=f'выбрать авто'),
            InlineKeyboardButton(text='⏩', callback_data=f'кол_след')
        ]

        car_collection_menu = \
            InlineKeyboardMarkup(row_width=1,
                                 inline_keyboard=[
                                     first_row,
                                     second_row,
                                     [
                                         InlineKeyboardButton(text='↩️ Назад',
                                                              callback_data=f'кол-выбрать_')
                                     ],
                                 ],
                                 )
        return car_collection_menu

    # меню для карточки автомобиля
    @staticmethod
    def get_card_picture_menu(side):
        card_picture_menu = \
            InlineKeyboardMarkup(row_width=1,
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='🏠 Гараж',
                                                              callback_data=f'в гараж_'),
                                         InlineKeyboardButton(text='🔄 Повернуть',
                                                              callback_data=f'повернуть карточку_{side}')
                                     ],
                                     [
                                         InlineKeyboardButton(text='↩️ Назад',
                                                              callback_data=f'кол_назад')
                                     ]
                                 ]
                                 )
        return card_picture_menu

    # меню для гаража
    garage_menu = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [
            InlineKeyboardButton(text='💬 Показать меню', callback_data='показать меню_')
        ],
        [
            InlineKeyboardButton(text='↩️ Назад', callback_data=f'выбрать авто')
        ]
    ])

    @staticmethod
    def get_garage_menu_2(garage_menu_index=0):
        if garage_menu_index == 0:
            callback_data = 'гар-инфо'
        elif garage_menu_index == 1:
            callback_data = 'гар-тюнинг'
        elif garage_menu_index == 2:
            callback_data = 'гар-шины'
        else:
            callback_data = 'гар-бусты'

        garage_menu_2 = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [
                InlineKeyboardButton(text='⬅️', callback_data=f'гар_влево'),
                InlineKeyboardButton(text='✅ Выбрать', callback_data=callback_data),
                InlineKeyboardButton(text='➡️', callback_data=f'гар_вправо'),
            ],
            [
                InlineKeyboardButton(text='↩️ Назад', callback_data=f'в гараж_')
            ]
        ])

        return garage_menu_2

    # меню для тюнинга
    @staticmethod
    def get_autoshop_menu(show_prices=0):
        first_row = [
            InlineKeyboardButton(text='⬅️', callback_data=f'тюн_влево_'),
            InlineKeyboardButton(text='➡️', callback_data=f'тюн_вправо_'),
            InlineKeyboardButton(text='⬆️', callback_data=f'тюн_вверх_'),
            InlineKeyboardButton(text='⬇️', callback_data=f'тюн_вниз_')
        ]

        caption = '💷 Цены' if not show_prices else '🔧 Детали'
        second_row = [
            InlineKeyboardButton(text=caption,
                                 callback_data=f'тюн-цены_'),
            InlineKeyboardButton(text='✅ Выбрать',
                                 callback_data=f'тюн-выбрать_')
        ]

        autoshop_menu = \
            InlineKeyboardMarkup(row_width=1,
                                 inline_keyboard=[
                                     first_row,
                                     second_row,
                                     [
                                         InlineKeyboardButton(text='↩️ Назад',
                                                              callback_data=f'показать меню_')
                                     ],
                                 ],
                                 )
        return autoshop_menu

    # меню для детали тюнинга
    @staticmethod
    def get_car_part_menu(car_part_status: int):
        car_part_statuses = {
            0: '💵 Купить',
            1: '❌ Снять',
            2: '✅ Установить'
        }

        car_part_menu = \
            InlineKeyboardMarkup(row_width=1,
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text=car_part_statuses[car_part_status],
                                                              callback_data=f'установить-деталь'),
                                         InlineKeyboardButton(text='🔧 Характеристики',
                                                              callback_data=f'установить-деталь')
                                     ],
                                     [
                                         InlineKeyboardButton(text='↩️ Назад',
                                                              callback_data=f'тюн_назад'),
                                     ]
                                 ]
                                 )
        return car_part_menu

    # меню для выбора шин
    tires_menu = \
        InlineKeyboardMarkup(row_width=1,
                             inline_keyboard=[
                                 [
                                     InlineKeyboardButton(text='⬅️', callback_data=f'шин_влево_'),
                                     InlineKeyboardButton(text='✅ Выбрать', callback_data=f'шин-выбрать_'),
                                     InlineKeyboardButton(text='➡️', callback_data=f'шин_вправо_')
                                 ],
                                 [
                                     InlineKeyboardButton(text='↩️ Назад',
                                                          callback_data=f'показать меню_')
                                 ]
                             ]
                             )

    tires_managment_menu = \
        InlineKeyboardMarkup(row_width=1,
                             inline_keyboard=[
                                 [
                                     InlineKeyboardButton(text='💷 Купить', callback_data=f'купить-шины'),
                                 ],
                                 [
                                     InlineKeyboardButton(text='↩️ Назад',
                                                          callback_data=f'шин_назад')
                                 ]
                             ]
                             )

