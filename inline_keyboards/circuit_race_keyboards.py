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
