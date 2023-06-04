import random

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import cursor, get_service_data


class RaceInlineKeyboard:
    # меню поиска
    search_menu = InlineKeyboardMarkup(row_width=1,
                                       inline_keyboard=[
                                           [
                                               InlineKeyboardButton(text='❌ Отменить поиск',
                                                                    callback_data='отменить-поиск')
                                           ]
                                       ],
                                       )

    # меню подтверждения гонки
    conf_menu_accept = InlineKeyboardMarkup(row_width=1,
                                            inline_keyboard=[
                                                [
                                                    InlineKeyboardButton(text='✅ Принять',
                                                                         callback_data='подтверждение-гонки_1'),
                                                    InlineKeyboardButton(text='❌ Отменить',
                                                                         callback_data='подтверждение-гонки_2')
                                                ]
                                            ],
                                            )

    conf_menu_waiting = InlineKeyboardMarkup(row_width=1,
                                             inline_keyboard=[
                                                 [
                                                     InlineKeyboardButton(text='⏳ Ждём остальных...',
                                                                          callback_data='ожидание')
                                                 ]
                                             ],
                                             )

    circuit_choice_menu = InlineKeyboardMarkup(row_width=1,
                                               inline_keyboard=[
                                                   [
                                                       InlineKeyboardButton(text='⬆️ Трасса 1',
                                                                            callback_data='выбрать-трассу_0'),
                                                       InlineKeyboardButton(text='⬆️ Трасса 2',
                                                                            callback_data='выбрать-трассу_1')
                                                   ]
                                               ],
                                               )

    start_tires_choice_menu = InlineKeyboardMarkup(row_width=1,
                                                   inline_keyboard=[
                                                       [
                                                           InlineKeyboardButton(text='⬅️',
                                                                                callback_data='стартовые-шины_влево'),
                                                           InlineKeyboardButton(text='✅ Выбрать',
                                                                                callback_data='стартовые-шины_выбрать'),
                                                           InlineKeyboardButton(text='➡️',
                                                                                callback_data='стартовые-шины_вправо')
                                                       ]
                                                   ],
                                                   )

    loading_race_menu = InlineKeyboardMarkup(row_width=1,
                                             inline_keyboard=[
                                                 [
                                                     InlineKeyboardButton(text='⏳ Загружаем гонку...',
                                                                          callback_data='ожидание')
                                                 ]
                                             ],
                                             )

    car_choice_menu = InlineKeyboardMarkup(row_width=1,
                                           inline_keyboard=[
                                               [
                                                   InlineKeyboardButton(text='⬅️',
                                                                        callback_data='автомобиль-для-гонки_влево'),
                                                   InlineKeyboardButton(text='✅',
                                                                        callback_data='автомобиль-для-гонки_выбрать'),
                                                   InlineKeyboardButton(text='➡️',
                                                                        callback_data='автомобиль-для-гонки_вправо')
                                               ],
                                               [
                                                   InlineKeyboardButton(text='🔄 Повернуть',
                                                                        callback_data='автомобиль-для-гонки_повернуть')
                                               ]
                                           ],
                                           )

    overtaking_menu = InlineKeyboardMarkup(row_width=1,
                                           inline_keyboard=[
                                               [
                                                   InlineKeyboardButton(text='🟢', callback_data='обг_1'),
                                                   InlineKeyboardButton(text='🟡', callback_data='обг_2'),
                                                   InlineKeyboardButton(text='🟠', callback_data='обг_3'),
                                                   InlineKeyboardButton(text='🔴', callback_data='обг_4')
                                               ]
                                           ],
                                           )

    @staticmethod
    def get_event_menu(cell_color_amounts: list, cell_amount: int = 12):
        colors = [0, 1, 2]
        cells = []
        for i in range(cell_amount):
            cell = random.choice(colors)
            cells.append(cell)
            cell_color_amounts[cell] -= 1
            if not cell_color_amounts[cell]:
                colors.remove(cell)

        first_row = []
        second_row = []

        first_row_hid = []
        second_row_hid = []

        emoji = {
            0: '🔴',
            1: '🟡',
            2: '🟢'
        }

        for i in range(cell_amount):
            cell = cells[i]
            button = InlineKeyboardButton(text=emoji[cell],
                                          callback_data=f'трасса-событ_занос_{cell}_{random.randint(10, 10000)}')
            hidden_button = InlineKeyboardButton(text='❔',
                                                 callback_data=f'трасса-событ_занос_{cell}_{random.randint(10, 10000)}')
            if i < cell_amount // 2:
                first_row.append(button)
                first_row_hid.append(hidden_button)
            else:
                second_row.append(button)
                second_row_hid.append(hidden_button)

        event_menu = InlineKeyboardMarkup(row_width=1,
                                          inline_keyboard=[
                                              first_row,
                                              second_row
                                          ],
                                          )
        hidden_event_menu = InlineKeyboardMarkup(row_width=1,
                                                 inline_keyboard=[
                                                     first_row_hid,
                                                     second_row_hid
                                                 ],
                                                 )

        return hidden_event_menu, event_menu
