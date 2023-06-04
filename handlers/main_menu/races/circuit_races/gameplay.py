import os.path
import asyncio
import random

from aiogram.types import InputFile, CallbackQuery, InputMedia, Message

from loader import dp, bot, update_current_message_id, update_service_data, get_service_data
from inline_keyboards import RaceInlineKeyboard
from useful_function.generate_race_pictures import *
from useful_function.generate_other_pictures import *
from .game import *
from .events import do_overtaking, uncontrollable_skid
from useful_function.calculating import *
from useful_function.for_cars import *
from useful_function.randomizer import *


user_readiness = dict()
choosen_cars = dict()
choosen_car_ids = dict()
priority_dices = dict()
event_bonuses = dict()
users_score = dict()
users_dices = dict()


async def waiting_players(user_id, race_id):
    global user_readiness
    while not all(user_readiness[race_id].values()):
        user_readiness[race_id][user_id] = 1
        await asyncio.sleep(0.1)
    return True


def set_players_readiness(race_id: int, readiness: int):
    global user_readiness
    users = list(user_readiness[race_id].keys())
    for user_id in users:
        user_readiness[race_id][user_id] = readiness


async def set_up_global_variables(race_id):
    global choosen_cars
    # if not choosen_cars.get(race_id, False):
    #     choosen_cars[race_id] = dict()


async def show_loading_window(user_id, race_id):
    circuit_id = cursor.execute("SELECT race_circuit FROM races WHERE id = ?", (race_id,)).fetchone()[0]

    path = f'images/race_circuits/{circuit_id}/loading.jpg'
    photo = InputFile(path)

    msg = await bot.send_photo(user_id, photo, reply_markup=RaceInlineKeyboard.loading_race_menu)
    await asyncio.sleep(5)
    await msg.delete()


async def play_race(user_id, race_id):
    global choosen_cars
    global choosen_car_ids
    global priority_dices
    global users_score
    global users_dices
    global event_bonuses

    users_score[race_id] = dict()
    users_dices[race_id] = dict()
    event_bonuses[race_id] = dict()

    user_readiness[race_id][user_id] = 0

    circuit_id = cursor.execute("SELECT race_circuit FROM races WHERE id = ?", (race_id,)).fetchone()[0]
    race_map = cursor.execute("SELECT elements FROM race_circuits WHERE id = ?", (circuit_id,)).fetchone()[0].split('_')
    race_map = [0] + race_map

    main_username = cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()[0]

    map_priority_dices = priority_dices.get(race_id, False)
    if not map_priority_dices:
        map_priority_dices = [random.randint(1, 6) for _ in range(len(race_map))]
        priority_dices[race_id] = map_priority_dices

    laps = cursor.execute("SELECT laps FROM races WHERE id = ?", (race_id,)).fetchone()[0]

    # score_caption = f"</b>--- Распределение очков: ---</b>\n\n" \
    #                 f""

    map_image_path = generate_race_map(race_id, user_id, 0, laps, 1)
    photo = InputFile(map_image_path)

    race_map_msg = await bot.send_photo(user_id, photo)
    os.remove(map_image_path)

    user_cars = cursor.execute("SELECT car_1, car_2, car_3, car_4 FROM user_car_deck WHERE user_id = ?",
                               (user_id,)).fetchone()
    user_deck = [i for i in user_cars]

    if await waiting_players(user_id, race_id):
        map_priority_dices = priority_dices[race_id]
        index = 0
        for circuit_element in race_map:
            circuit_element = int(circuit_element)
            choosen_cars[user_id] = [0, 0]

            priority_dice = map_priority_dices[index]

            score_caption = ''
            places = {
                1: '🏅',
                2: '🥈',
                3: '🥉',
                4: '4️⃣',
                5: '5️⃣',
                6: '6️⃣'
            }
            race_members = list(user_readiness[race_id].keys())
            sorted_users = dict()
            for i in range(len(race_members)):
                user = race_members[i]
                if users_score[race_id].get(user):
                    all_user_score = sum(sc[0] for sc in users_score[race_id][user])
                else:
                    all_user_score = 0
                sorted_users[user] = all_user_score

            sorted_users = sorted(sorted_users.items(), key=lambda item: item[1], reverse=True)
            for i in range(len(sorted_users)):
                user = sorted_users[i][0]
                username = cursor.execute("SELECT username FROM users WHERE id = ?", (user,)).fetchone()[0]

                score_caption += f'{places[i + 1]} <b>{username}:</b> {sorted_users[i][1]} очк.\n'

            element_name = elements_names[circuit_element]
            caption = f'-                         -\n' \
                      f'{score_caption}\n\n' \
                      f'<b>{elements_emoji[circuit_element]} Элемент трассы:</b> {element_name}\n' \
                      f'<b>🎲 Приоритетные очки:</b> {priority_dice}\n\n' \
                      f'Выберите автомобиль:\n' \
                      f'-                         -'

            card_path = os.path.join(f'images/for_saves/races/{race_id}_{user_id}_car{user_deck[0]}.png')
            photo = InputFile(card_path)

            capt_msg = await bot.send_message(user_id, caption)
            msg = await bot.send_photo(user_id, photo, reply_markup=RaceInlineKeyboard.car_choice_menu)

            ind = 0
            backside = False
            user_readiness[race_id][user_id] = 0
            for i in range(15000):
                if choosen_cars[user_id][0] != ind or (choosen_cars[user_id][1] == 0 and backside):
                    backside = False
                    ind = choosen_cars[user_id][0]

                    card_path = os.path.join(f'images/for_saves/races/{race_id}_{user_id}_car{user_deck[ind]}.png')
                    photo = InputFile(card_path)
                    media = InputMedia(media=photo)

                    msg = await bot.edit_message_media(media, user_id, msg.message_id,
                                                       reply_markup=RaceInlineKeyboard.car_choice_menu)
                elif choosen_cars[user_id][1] == 2 and not backside:
                    backside = True
                    car_tires = tires[race_id][user_id][user_deck[ind]]
                    image_path = generate_card_picture(user_id, user_deck[ind], backside=True, tires=car_tires)
                    media = InputMedia(media=InputFile(image_path))

                    msg = await bot.edit_message_media(media, user_id, msg.message_id,
                                                       reply_markup=RaceInlineKeyboard.car_choice_menu)
                    os.remove(image_path)

                elif choosen_cars[user_id][1] == 1:
                    break

                await asyncio.sleep(0.1)

            car_index = choosen_cars[user_id][0]
            car_id = user_deck[car_index]
            await msg.delete()

            dice = random.randint(1, 6)
            users_dices[race_id][user_id] = dice
            msg = await bot.send_sticker(user_id, dice_sticker_ids[dice])
            await asyncio.sleep(4)
            await msg.delete()

            if not choosen_car_ids.get(race_id, False):
                choosen_car_ids[race_id] = dict()
            choosen_car_ids[race_id][user_id] = car_id

            tires[race_id][user_id][car_id][1] = \
                change_tires_wear(tires[race_id][user_id][car_id], race_id, circuit_element)

            driving_exp = cursor.execute("SELECT driving_exp FROM users_cars WHERE (user_id, car_id) = (?, ?)",
                                         (user_id, car_id)).fetchone()[0] / 10
            handling = calculate_characteristic_bar_length(car_id, 100, None, user_id)[2]
            overall_handling = int(handling + driving_exp)

            if overall_handling < 50:
                event_chance = 20
            elif 50 <= overall_handling < 60:
                event_chance = 15
            elif 70 <= overall_handling < 80:
                event_chance = 13
            else:
                event_chance = 10

            set_players_readiness(race_id, 0)
            if get_result_by_chance(event_chance):
                users = list(user_readiness[race_id].keys())
                text = f"❗️ Игрок <b>{main_username}</b> попал в занос"
                messages = []
                for user in users:
                    if user != user_id:
                        msg_to_delete = await bot.send_message(user, text)
                        messages.append(msg_to_delete)

                event_bonus = await uncontrollable_skid(user_id, car_id)

                msg_index = 0
                for user in users:
                    if user != user_id:
                        await bot.delete_message(user, messages[msg_index].message_id)
                        msg_index += 1
            else:
                event_bonus = 1

            event_bonuses[race_id][user_id] = event_bonus

            msg = await msg.answer("⏳ Ждем остальных игроков...")

            if await waiting_players(user_id, race_id):
                move = 0
                users_current_score = dict()
                update_driving_experience(user_id, car_id)
                for user in list(user_readiness[race_id].keys()):
                    cur_car_id = choosen_car_ids[race_id][user]
                    cur_dice = users_dices[race_id][user]

                    characteristics_bonus = \
                        calculate_score(race_id, user, circuit_element, cur_car_id,
                                        tires[race_id][user][cur_car_id])

                    dice_dif = abs(priority_dice - cur_dice)
                    if dice_dif > 3:
                        dice_dif = 6 - dice_dif
                    if dice_dif == 0:
                        dice_bonus = 1.3
                    elif dice_dif == 1:
                        dice_bonus = 1.2
                    elif dice_dif == 2:
                        dice_bonus = 1.1
                    else:
                        dice_bonus = 1

                    event_bonus = event_bonuses[race_id][user]

                    if user == user_id:
                        score = int(characteristics_bonus * dice_bonus * event_bonus)
                        user_score = users_score[race_id].get(user)
                        if not user_score:
                            user_score = [[score, cur_car_id]]
                        else:
                            user_score.append([score, cur_car_id])
                        users_score[race_id][user] = user_score

                    image_path = \
                        generate_scoring_window(race_id, user, cur_car_id, tires[race_id][user][cur_car_id][0],
                                                circuit_element, cur_dice, priority_dice, characteristics_bonus,
                                                dice_bonus, event_bonus)
                    photo = InputFile(image_path)

                    await msg.delete()
                    msg = await bot.send_photo(user_id, photo)
                    os.remove(image_path)
                    await asyncio.sleep(15)

                    move += 1

                    all_user_score = sum(sc[0] for sc in users_score[race_id][user])
                    current_score = int(characteristics_bonus * dice_bonus * event_bonus)
                    users_current_score[user] = [all_user_score - current_score, current_score]

            await msg.delete()

            set_players_readiness(race_id, 0)
            for user_1 in list(user_readiness[race_id].keys()):
                for user_2 in list(user_readiness[race_id].keys()):
                    if user_1 != user_2:
                        if users_current_score[user_2][0] > users_current_score[user_1][0]:
                            theoretical_score_1 = users_current_score[user_1][0] + users_current_score[user_1][1]
                            theoretical_score_2 = users_current_score[user_2][0] + users_current_score[user_2][1]
                            if 1 <= theoretical_score_1 - theoretical_score_2 <= 15:
                                data = {
                                    user_1: choosen_car_ids[race_id][user_1],
                                    user_2: choosen_car_ids[race_id][user_2]
                                }
                                penalty = max(users_current_score[user_2][0], users_current_score[user_2][1]) // 4
                                winner = await do_overtaking(race_id, user_id, data, [users_current_score[user_1][0],
                                                                                      users_current_score[user_2][0]],
                                                             penalty)
                                if user_1 == user_id:
                                    if user_1 == winner:
                                        users_score[race_id][user_2].pop(-1)
                                        users_score[race_id][user_2].append([theoretical_score_1 - 10, data[user_2]])
                                    else:
                                        users_score[race_id][user_1].pop(-1)
                                        users_score[race_id][user_1].append([theoretical_score_2 - 10, data[user_1]])

            await capt_msg.delete()

            map_image_path = generate_race_map(race_id, user_id, 0, laps, index + 2)
            photo = InputFile(map_image_path)
            media = InputMedia(media=photo)

            try:
                race_map_msg = await bot.edit_message_media(media, user_id, race_map_msg.message_id)
            except:
                try:
                    race_map_msg = await bot.send_photo(user_id, photo)
                except:
                    ...

            os.remove(map_image_path)

            priority_dices[race_id] = None

            index += 1


@dp.message_handler(text="/game")
async def command_game(message: Message):
    user_id = message.from_user.id

    image = InputFile('images/design/loadings/circuit_load.jpg')
    inline_keyboard = RaceInlineKeyboard.search_menu

    msg = await bot.send_photo(message.chat.id, photo=image, reply_markup=inline_keyboard)

    response = await search_race(user_id, msg)
    if response == 1:
        await msg.delete()
        conf_id = get_service_data(user_id, 'race_confirmation_id')
        # race_id = await game_confirmation(user_id, conf_id)
        # print(race_id)
        race_id = 87
        if race_id:
            global user_readiness
            if not user_readiness.get(race_id, False):
                user_readiness[race_id] = dict()

            user_readiness[race_id][user_id] = 0
            # await show_race_members(user_id, race_id)
            # await circuit_voting(user_id, race_id)
            # await show_race_info(user_id, race_id)
            await choose_start_tires(user_id, race_id)
            await show_loading_window(user_id, race_id)
            generate_race_pictures(user_id, race_id)
            await waiting_players(user_id, race_id)
            await play_race(user_id, race_id)


@dp.callback_query_handler(text_contains='автомобиль-для-гонки_')
async def decline_search(call: CallbackQuery):
    await call.answer()

    user_id = call.from_user.id
    direction = call.data.split('_')[1]
    current_index = choosen_cars[user_id][0]
    if direction == 'вправо':
        choosen_cars[user_id][1] = 0
        current_index += 1
        if current_index > 3:
            current_index = 0
    elif direction == 'влево':
        choosen_cars[user_id][1] = 0
        current_index -= 1
        if current_index < 0:
            current_index = 3
    elif direction == 'выбрать':
        choosen_cars[user_id][1] = 0
        choosen_cars[user_id][1] = 1
    elif direction == 'повернуть':
        if choosen_cars[user_id][1] == 0:
            choosen_cars[user_id][1] = 2
        elif choosen_cars[user_id][1] == 2:
            choosen_cars[user_id][1] = 0

    choosen_cars[user_id][0] = current_index
