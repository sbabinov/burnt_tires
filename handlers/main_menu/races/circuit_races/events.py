import os.path
import asyncio
import random

from aiogram.types import InputFile, CallbackQuery, InputMedia, Message

from loader import dp, bot, update_current_message_id, update_service_data, get_service_data
from inline_keyboards import RaceInlineKeyboard
from useful_function.generate_race_pictures import *
from useful_function.generate_other_pictures import *
from useful_function.randomizer import *

overtakings = dict()
overtaking_dices = dict()
user_readiness = dict()
user_events = dict()
penalties = dict()


async def waiting_players(user_id, race_id):
    global user_readiness
    while not all(user_readiness[race_id].values()):
        user_readiness[race_id][user_id] = 1
        await asyncio.sleep(0.1)
    return True


async def overtaking_events(race_id, data: dict, attack_power, defend_power, penalty):
    global penalties

    body_parts_rus = {
        'front': 'передняя часть',
        'rear': 'задняя часть',
        'right_side': 'правая часть',
        'left_side': 'левая часть'
    }

    attacker = list(data.keys())[0]
    defender = list(data.keys())[1]

    attack_event_chance = 1
    defend_event_chance = 1

    for i in range(attack_power):
        attack_event_chance *= 1.5
    for i in range(defend_power):
        defend_event_chance *= 1.5

    general_event_chance = int(attack_event_chance * defend_event_chance / 2) * 10
    general_event_chance = 100
    messages_to_delete = []
    if get_result_by_chance(general_event_chance):
        for user in attacker, defender:
            damage = random.randint(5, 15)
            if user == attacker:
                damaged_part = random.choice(['front', 'left_side', 'right_side'])
            else:
                if damaged_part == 'front':
                    damaged_part = 'rear'
                elif damaged_part == 'left_side':
                    damaged_part = 'right_side'
                elif damaged_part == 'right_side':
                    damaged_part = 'left_side'

            if user == attacker:
                texts = [
                    "Эй, эй, аккуратнее при обгоне! Автомобиль будем чинить за свои деньги!",
                    f"При атаке повредилась {body_parts_rus[damaged_part]}, не торопись в следующий раз!",
                    "Настойчивость - это хорошо, но нужно знать меру! Два поломанных автомобиля того не стоят!"
                ]
            else:
                texts = [
                    f"Автомобиль повредился... Кажется, его {body_parts_rus[damaged_part]}...",
                    "Столкновение с соперником! С тобой всё в порядке? Отлично...",
                    "Упс... Кажется, после гонки придётся чинить автомобиль..."
                ]

            body_state = cursor.execute(f"SELECT {damaged_part} FROM cars_body_state WHERE (user_id, car_id) = (?, ?)",
                                        (user, data[user])).fetchone()[0]
            body_state -= damage

            cursor.execute(f"UPDATE cars_body_state SET {damaged_part} = ? WHERE (user_id, car_id) = (?, ?)",
                           (body_state, user, data[user]))
            connection.commit()

            text = random.choice(texts)
            text_part = "⚙️ <b><i>Механик:</i></b>\n\n"
            text = text_part + text

            msg = await bot.send_message(user, text)
            messages_to_delete.append({user: msg.message_id})

        culprits = []
        if attack_power != defend_power:
            if attack_power > defend_power:
                culprits.append(attacker)
            else:
                culprits.append(defender)
        else:
            culprits.append(attacker)
            culprits.append(defender)

        for culprit in culprits:
            penalties[culprit] = penalty

        users = list(user_readiness[race_id].keys())
        for user in users:
            if len(culprits) == 1:
                username = cursor.execute("SELECT username FROM users WHERE id = ?", (user,)).fetchone()[0]
                text = f"❗️ {username.capitalize()} получает штраф {penalty} очк. за столкновение"
            else:
                culprit_1 = culprits[0]
                culprit_2 = culprits[1]

                username_1 = cursor.execute("SELECT username FROM users WHERE id = ?", (culprit_1,)).fetchone()[0]
                username_2 = cursor.execute("SELECT username FROM users WHERE id = ?", (culprit_2,)).fetchone()[0]

                text = f"❗️ {username_1.capitalize()} и {username_2} получают штраф {penalty} очк. за столкновение"

            msg = await bot.send_message(user, text)
            messages_to_delete.append({user: msg.message_id})

        await asyncio.sleep(3)
        for msg in messages_to_delete:
            user = list(msg.keys())[0]
            await bot.delete_message(user, msg[user])

        return penalty
    return False


async def get_random_event(user_id, cell_color, car_id):
    car_brand = cursor.execute("SELECT car_brand FROM cars WHERE id = ?", (car_id,)).fetchone()[0]
    car_brand = cars_brands[car_brand]

    if cell_color == 2:
        texts = [
            "Фух! Ты довольно быстро справился с заносом, не потеряв много времени. Так держать!",
            "Отлично, теперь все 4 колеса цепляются за трассу как надо.",
            f"Осторожно, {car_brand} иногда заносит, аккуратно работай газом... Молодец, автомобиль выправился!",
            "Ой-ой-ой, не спеши, занос всегда коварен!"
        ]
        numbers = [i / 100 for i in range(91, 98)]
        event_bonus = random.choice(numbers)
        text = random.choice(texts)
    elif cell_color == 1:
        texts = [
            "Неудачный поворот... Постарайся скорее забыть об этом и продолжай сражаться.",
            "У каждого бывают ошибки, не унывай! Главное - место на финише!",
            f"Кажется, наш {car_brand} попал в занос... Повезло, что не улетели в отбойник.",
            "Упс, неприятная ситуация... Не обращай внимания, сосредоточься на следующем повороте."
        ]
        numbers = [i / 100 for i in range(51, 61)]
        event_bonus = random.choice(numbers)
        text = random.choice(texts)
    else:
        numbers = [i for i in range(11, 22)]
        event_bonus = random.choice(numbers)

        body_parts = ['front', 'rear', 'right_side', 'left_side']
        body_parts_rus = {
            'front': 'передняя часть',
            'rear': 'задняя часть',
            'right_side': 'правая часть',
            'left_side': 'левая часть'
        }
        damaged_body_part = random.choice(body_parts)

        texts = [
            "... слышишь меня? С тобой всё в порядке? Отлично... А вот автомобилю несладко пришлось...",
            f"Аккуратнее, рядом отбойник... Кажется, у автомобиля повредилась {body_parts_rus[damaged_body_part]}...",
            f"{body_parts_rus[damaged_body_part].capitalize()} автомобиля пострадала, нельзя допустить повторного "
            f"столкновения.",
            f"Автомобиль пока на ходу, но его {body_parts_rus[damaged_body_part]} не выглядит целой..."
        ]

        current_state = \
            cursor.execute(f"SELECT {damaged_body_part} FROM cars_body_state WHERE (user_id, car_id) = (?, ?)",
                           (user_id, car_id)).fetchone()[0]

        if current_state > 22:
            current_state -= int(event_bonus)

        cursor.execute(f"UPDATE cars_body_state SET {damaged_body_part} = ? WHERE (user_id, car_id) = (?, ?)",
                       (current_state, user_id, car_id))
        connection.commit()

        event_bonus /= 100
        text = random.choice(texts)

    text_part = "⚙️ <b><i>Механик:</i></b>\n\n"
    text = text_part + text

    msg = await bot.send_message(user_id, text)
    await asyncio.sleep(3)
    await msg.delete()

    return event_bonus


async def uncontrollable_skid(user_id: int, car_id: int):
    driving_exp = cursor.execute("SELECT driving_exp FROM users_cars WHERE (user_id, car_id) = (?, ?)",
                                 (user_id, car_id)).fetchone()[0] / 10
    handling = calculate_characteristic_bar_length(car_id, 100, None, user_id)[2]

    overall_handling = int(handling + driving_exp)

    green_cells = overall_handling // 20
    red_cells = 12 - overall_handling // 9
    if red_cells > 4:
        red_cells = 4
    yellow_cells = 12 - green_cells - red_cells

    cells = [red_cells, yellow_cells, green_cells]
    hidden_menu, visible_menu = RaceInlineKeyboard.get_event_menu(cells)

    photo = InputFile(os.path.join('images/races/events/uncontrollable_skid.jpg'))

    msg = await bot.send_photo(user_id, photo, reply_markup=hidden_menu)
    while user_events.get(user_id, -1) not in [0, 1, 2]:
        await asyncio.sleep(0.1)

    choosen_cell = user_events[user_id]
    del user_events[user_id]
    await msg.edit_reply_markup(reply_markup=visible_menu)
    await asyncio.sleep(2)
    event_bonus = await get_random_event(user_id, choosen_cell, car_id)
    await msg.delete()

    return event_bonus


async def do_overtaking(race_id, user_id: int, data: dict, score: list, penalty: int):
    global overtakings
    global overtaking_dices
    global user_readiness

    overtaking_agression = {
        1: '🟢',
        2: '🟡',
        3: '🟠',
        4: '🔴'
    }

    if not user_readiness.get(race_id, False):
        user_readiness[race_id] = dict()

    attacker, car_1 = list(data.items())[0]
    defender, car_2 = list(data.items())[1]

    user_readiness[race_id][attacker] = 0
    user_readiness[race_id][defender] = 0

    attacker_username = cursor.execute("SELECT username FROM users WHERE id = ?", (attacker,)).fetchone()[0]
    defender_username = cursor.execute("SELECT username FROM users WHERE id = ?", (defender,)).fetchone()[0]

    attacker_score = score[0]
    defender_score = score[1]

    main_caption = f"⚔️ <b>Атакует:</b> {attacker_username} <i>({attacker_score} очк.)</i>\n" \
                   f"🛡 <b>Защищается:</b> {defender_username} <i>({defender_score} очк.)</i>\n\n"

    inline_keyboard = None
    if user_id == attacker:
        caption_part = "Выберите агрессивность атаки:"
        inline_keyboard = RaceInlineKeyboard.overtaking_menu
        overtakings[user_id] = None
    elif user_id == defender:
        caption_part = "Ждём выбора соперника..."
        overtakings[user_id] = None
    else:
        caption_part = f"<b>{attacker_username}</b> выбирает агрессивность атаки..."

    caption = main_caption + caption_part

    image_path = generate_overtaking_window(data)
    image = InputFile(image_path)

    msg = await bot.send_photo(user_id, image, caption=caption, reply_markup=inline_keyboard)
    os.remove(image_path)

    if await waiting_players(user_id, race_id):
        while overtakings[attacker] is None:
            await asyncio.sleep(0.1)

    inline_keyboard = None
    user_readiness[race_id][user_id] = 0
    if user_id == attacker:
        attacker_dice = random.randint(1, 6)
        overtaking_dices[user_id] = attacker_dice

        dice_msg = await bot.send_sticker(user_id, dice_sticker_ids[attacker_dice])
        await asyncio.sleep(4)
        await dice_msg.delete()

        caption_part = f"<b>Атака:</b> {overtaking_agression[overtakings[attacker]]}\n" \
                       f"Ждём выбора соперника..."
    else:
        await asyncio.sleep(3)

    if await waiting_players(user_id, race_id):
        if user_id == defender:
            caption_part = f"<b>Атака:</b> {overtaking_agression[overtakings[attacker]]}\n" \
                           f"Выберите агрессивность защиты:"
            inline_keyboard = RaceInlineKeyboard.overtaking_menu
        else:
            caption_part = f"<b>Атака:</b> {overtaking_agression[overtakings[attacker]]}\n" \
                           f"<b>{defender_username}</b> выбирает агрессивность защиты..."

    caption = main_caption + caption_part
    msg = await msg.edit_caption(caption=caption, reply_markup=inline_keyboard)

    while overtakings[defender] is None:
        await asyncio.sleep(0.1)

    user_readiness[race_id][user_id] = 0
    if user_id == defender:
        defender_dice = random.randint(1, 6)
        overtaking_dices[user_id] = defender_dice

        dice_msg = await bot.send_sticker(user_id, dice_sticker_ids[defender_dice])
        await asyncio.sleep(4)
        await dice_msg.delete()
    else:
        await asyncio.sleep(3)

    if await waiting_players(user_id, race_id):
        attacker_dice = overtaking_dices[attacker]
        defender_dice = overtaking_dices[defender]

    attacker_agression = overtakings[attacker]
    defender_agression = overtakings[defender]

    dice_values = {
        1: (2, 6, 3, 5, 4),
        2: (3, 1, 4, 6, 5),
        3: (4, 2, 5, 1, 6),
        4: (5, 3, 6, 2, 1),
        5: (6, 4, 1, 3, 2),
        6: (1, 5, 2, 4, 3),
    }

    win_dice_values = []
    dif = abs(defender_agression - attacker_agression)
    if attacker_agression >= defender_agression:
        for i in range(dif + 2):
            win_dice_values.append(dice_values[defender_dice][i])
    elif attacker_agression < defender_agression:
        if dif < 3:
            for i in range(3 - dif):
                win_dice_values.append(dice_values[defender_dice][i])

    successful_scores = ', '.join([str(i) for i in win_dice_values])

    if await waiting_players(user_id, race_id):
        caption = f"⚔️ <b>Атака:</b> {overtaking_agression[attacker_agression]}, выпало <b>{attacker_dice}</b>\n" \
                  f"🛡 <b>Защита:</b> {overtaking_agression[defender_agression]}, выпало <b>{defender_dice}</b>\n\n" \
                  f"🎲 <b>Успешные очки для атаки:</b> {successful_scores}\n" \

        if user_id != attacker and user_id != defender:
            if attacker_dice in win_dice_values:
                caption_part = f"✅ <b>{attacker_username}</b> успешно обгоняет игрока <b>{defender_username}</b>!"
            else:
                caption_part = f"⛔️ <b>{defender_username}</b> успешно защищается от игрока <b>{attacker_username}</b>!"
        elif user_id == attacker:
            if attacker_dice in win_dice_values:
                caption_part = f"✅ <b>Вы</b> успешно обгоняете игрока <b>{defender_username}</b>!"
            else:
                caption_part = f"⛔️ <b>{defender_username}</b> успешно защищается!"
        else:
            if attacker_dice in win_dice_values:
                caption_part = f"❌ <b>Вас</b> успешно обгоняет игрок <b>{attacker_username}</b>!"
            else:
                caption_part = f"✅ <b>Вы</b> успешно защищаетесь от игрока <b>{attacker_username}</b>!"

        caption += caption_part
        msg = await msg.edit_caption(caption=caption, reply_markup=None)
        await asyncio.sleep(5)
        await msg.delete()

        user_readiness[race_id][user_id] = 0
        if user_id == attacker:
            await overtaking_events(race_id, data, attacker_agression - 1, defender_agression - 1, penalty)
        await waiting_players(user_id, race_id)

        winner = attacker if attacker_dice in win_dice_values else defender
        return winner


@dp.callback_query_handler(text_contains='обг_')
async def choose_overtaking_agression(call: CallbackQuery):
    await call.answer()

    user_id = call.from_user.id
    overtaking_agression = int(call.data.split('_')[1])

    if overtakings[user_id] is None:
        overtakings[user_id] = overtaking_agression


@dp.callback_query_handler(text_contains='трасса-событ_')
async def play_race_event(call: CallbackQuery):
    global user_events

    user_id = call.from_user.id
    event = call.data.split('_')[1]
    if event == 'занос':
        cell = call.data.split('_')[2]
        if user_events.get(user_id, -1) not in [0, 1, 2]:
            user_events[user_id] = int(cell)
