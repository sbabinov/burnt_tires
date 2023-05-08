from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    username = State()


class MainState(StatesGroup):
    main_state = State()

    brand_page_index = State()
    choose_brand_index = State()

