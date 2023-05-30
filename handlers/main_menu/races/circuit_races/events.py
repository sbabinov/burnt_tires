import os.path
import asyncio
import random

from aiogram.types import InputFile, CallbackQuery, InputMedia, Message

from loader import dp, bot, update_current_message_id, update_service_data, get_service_data
from inline_keyboards import RaceInlineKeyboard
from useful_function.generate_race_pictures import *
from useful_function.generate_other_pictures import *

overtakings = dict()
overtaking_dices = dict()
user_readiness = dict()


async def waiting_players(user_id, race_id):
    global user_readiness
    while not all(user_readiness[race_id].values()):
        user_readiness[race_id][user_id] = 1
        await asyncio.sleep(0.1)
    return True


async def do_overtaking(race_id, user_id: int, data: dict, score: list):
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

    events_chances = {
        1: 0.005,
        2: 0.02,
        3: 0.05,
        4: 0.1
    }

    attacker_agression = overtakings[attacker]
    defender_agression = overtakings[defender]

    general_chance = events_chances[attacker_agression] + events_chances[defender_agression]
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

        winner = attacker if attacker_dice in win_dice_values else defender
        return winner


@dp.callback_query_handler(text_contains='обг_')
async def choose_overtaking_agression(call: CallbackQuery):
    await call.answer()

    user_id = call.from_user.id
    overtaking_agression = int(call.data.split('_')[1])

    # if overtaking_type == 'атака':
    if overtakings[user_id] is None:
        overtakings[user_id] = overtaking_agression
