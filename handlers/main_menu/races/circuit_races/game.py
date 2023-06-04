import os.path
import asyncio
import random

from aiogram.types import InputFile, CallbackQuery, InputMedia, Message

from loader import dp, bot, update_current_message_id, update_service_data, get_service_data
from inline_keyboards import RaceInlineKeyboard
from useful_function.generate_race_pictures import *
from useful_function.generate_other_pictures import *

conf_images = dict()
race_images = dict()
voting_images = dict()
voting_images_2 = dict()
voting = dict()
reply_markups = dict()
ready_users = dict()


def get_race_members(race_id: int):
    members = cursor.execute("SELECT members FROM races WHERE id = ?", (race_id,)).fetchone()[0].split()
    members = [int(member) for member in members]
    return members


async def search_race(user_id: int, message_to_edit: Message):
    cursor.execute("INSERT INTO race_search VALUES (?, ?)", (user_id, 0))
    connection.commit()

    for second in range(60):
        users_in_search = cursor.execute("SELECT user_id FROM race_search").fetchall()
        users_in_search = users_in_search if users_in_search is None else [user[0] for user in users_in_search]

        if (not users_in_search) or (users_in_search and user_id not in users_in_search):
            return 1
        else:
            user_status = cursor.execute("SELECT race_type FROM race_search WHERE user_id = ?",
                                         (user_id,)).fetchone()[0]
            if user_status == -1:
                cursor.execute("DELETE FROM race_search WHERE user_id = ?", (user_id,))
                connection.commit()

                return -1

        if users_in_search and len(users_in_search) == 2:
            race_members = [users_in_search[0], users_in_search[1]]
            for member in race_members:
                cursor.execute("DELETE FROM race_search WHERE user_id = ?", (member,))
                connection.commit()

            current_confirmations = cursor.execute("SELECT id FROM race_confirmations").fetchall()
            if not current_confirmations:
                conf_id = 1
            else:
                conf_id = current_confirmations[-1][0] + 1

            confirmations = ''
            for member in race_members:
                update_service_data(member, 'race_confirmation_id', conf_id)
                confirmations += f'{member}-0 '

            cursor.execute("INSERT INTO race_confirmations VALUES (?, ?, ?)", (conf_id, confirmations[:-1], 0))
            connection.commit()

            return 1
        await asyncio.sleep(1)

        caption = f'-                                      -\n' \
                  f'⏳ Прошло: <b>{second} с</b>\n' \
                  f'-                                      -' \

        inline_keyboard = message_to_edit.reply_markup

        await bot.edit_message_caption(user_id, message_to_edit.message_id, caption=caption,
                                       reply_markup=inline_keyboard)
    else:
        cursor.execute("DELETE FROM race_search WHERE user_id = ?", (user_id,))
        connection.commit()
    return 0


async def game_confirmation(user_id: int, confirmations_id: int):
    global conf_images

    members_confirmations = cursor.execute("SELECT confirmations FROM race_confirmations WHERE id = ?",
                                           (confirmations_id,)).fetchone()[0]

    image_path = generate_confirmation_window(confirmations_id)
    photo = InputFile(image_path)

    inline_keyboard = RaceInlineKeyboard.conf_menu_accept

    msg = await bot.send_photo(user_id, photo, reply_markup=inline_keyboard)

    os.remove(image_path)
    update_current_message_id(user_id, msg.message_id)
    members_accept = set()
    for i in range(150):
        stop = True
        old_members_confirmations = members_confirmations
        members_confirmations = cursor.execute("SELECT confirmations FROM race_confirmations WHERE id = ?",
                                               (confirmations_id,)).fetchone()[0]

        for member in members_confirmations.split():
            member_id = int(member.split('-')[0])
            member_status = int(member.split('-')[1])

            if member_id == user_id and member_status == 1:
                inline_keyboard = RaceInlineKeyboard.conf_menu_waiting

            if member_status == 0:
                stop = False

            if member_status == 1:
                members_accept.add(member_id)

        if stop:
            break

        if old_members_confirmations != members_confirmations:
            try:

                image_path = conf_images.get(confirmations_id, False)
                if not image_path:
                    media = InputMedia(media=InputFile(generate_confirmation_window(confirmations_id)))
                    msg = await bot.edit_message_media(media, user_id, msg.message_id,
                                                       reply_markup=inline_keyboard)
                    conf_images[confirmations_id] = [msg.photo[-1].file_id]
                elif len(image_path) < len(members_accept) + 1:
                    media = InputMedia(media=InputFile(generate_confirmation_window(confirmations_id)))
                    msg = await bot.edit_message_media(media, user_id, msg.message_id,
                                                       reply_markup=inline_keyboard)
                    conf_images[confirmations_id] += [msg.photo[-1].file_id]
                else:
                    # media = InputMedia(media=InputFile(file_id))

                    await bot.edit_message_media(image_path[-1], user_id, msg.message_id)

            except:
                ...

        await asyncio.sleep(0.1)

    permission = True
    while True:
        finish = True
        members_confirmations = cursor.execute("SELECT confirmations FROM race_confirmations WHERE id = ?",
                                               (confirmations_id,)).fetchone()[0]
        members_confirmations_list = members_confirmations.split()
        members_list = [int(member.split('-')[0]) for member in members_confirmations.split()]

        for member in members_confirmations.split():
            member_id = int(member.split('-')[0])
            member_status = int(member.split('-')[1])

            if member_id == user_id and member_status == 0:
                members_confirmations_list.remove(member)
                members_confirmations_list.append(f'{member_id}-2')
                members_confirmations = ' '.join(members_confirmations_list)

                cursor.execute("UPDATE race_confirmations SET confirmations = ? WHERE id = ?",
                               (members_confirmations, confirmations_id))
                connection.commit()

            if member_status == 0:
                finish = False
            if member_status == 2:
                members_list.remove(member_id)
                permission = False

        if finish:
            break

        try:
            os.remove(image_path)
        except:
            ...

        await asyncio.sleep(1)

    # занесение новой гонки в БД
    if permission:
        members = ' '.join([str(member) for member in sorted(members_list)])

        race_id = cursor.execute("SELECT race_id FROM race_confirmations WHERE id = ?",
                                 (confirmations_id,)).fetchone()[0]
        if not race_id:
            current_races = cursor.execute("SELECT id FROM races").fetchall()
            if not current_races:
                race_id = 1
            else:
                race_id = current_races[-1][0] + 1

            cursor.execute("UPDATE race_confirmations SET race_id = ? WHERE id = ?", (race_id, confirmations_id))
            cursor.execute("INSERT INTO races VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (race_id, 'circuit', members, -1, '', 0, '', 0, 0))
            connection.commit()

        update_service_data(user_id, 'race_confirmation_id', race_id)

        await msg.delete()

        return race_id

    return False


async def show_race_members(user_id: int, race_id: int):
    global race_images
    race_members = get_race_members(race_id)

    for page_index in range(len(race_members) // 2 + (1 if len(race_members) % 2 != 0 else 0)):
        members_image_path = race_images.get(race_id, False)
        if not members_image_path:
            members_image_path = await generate_race_members_picture(race_id, page_index)
            image = InputFile(members_image_path)

            msg = await bot.send_photo(user_id, image)

            members_image_path = msg.photo[-1].file_id
            race_images[race_id] = [members_image_path]
        elif len(members_image_path) < (len(race_members) // 2 + (1 if len(race_members) % 2 != 0 else 0)):
            members_image_path = await generate_race_members_picture(race_id, page_index)
            image = InputFile(members_image_path)

            msg = await bot.send_photo(user_id, image)

            members_image_path = msg.photo[-1].file_id
            race_images[race_id] += [members_image_path]
        else:
            msg = await bot.send_photo(user_id, members_image_path[-1])

        await asyncio.sleep(4)
        await msg.delete()

    # if len(race_members) > 2:
    #     for page_index in range(1, len(race_members) // 2 + (1 if len(race_members) % 2 != 0 else 0)):
    #
    #         first_members_image_path = await generate_race_members_picture(race_id, page_index)
    #         image = InputFile(first_members_image_path)
    #
    #         await msg.delete()
    #         msg = await bot.send_photo(user_id, image)
    #
    #         await asyncio.sleep(4)


permissions = dict()


async def circuit_voting(user_id, race_id):
    global voting_images
    global voting_images_2
    global ready_users
    global reply_markups

    if not voting.get(race_id, False):
        voting[race_id] = {}
        circuits_for_choice = []
        circuit_ids = [circ[0] for circ in cursor.execute("SELECT id FROM race_circuits").fetchall()]
        for _ in range(2):
            circuit_id = random.choice(circuit_ids)
            circuit_ids.remove(circuit_id)
            circuits_for_choice.append(circuit_id)
            voting[race_id][circuit_id] = set()
    else:
        circuits_for_choice = list(voting[race_id].keys())

    image_path = voting_images.get(race_id)
    if not image_path:
        image_path = generate_circuit_choice_window(race_id, circuits_for_choice)
        voting_images[race_id] = image_path

    image = InputFile(image_path)
    inline_keyboard = RaceInlineKeyboard.circuit_choice_menu

    message = await bot.send_photo(user_id, image, reply_markup=inline_keyboard)
    reply_markups[user_id] = message.reply_markup

    votes = list(voting[race_id].values())
    for user in votes[0]:
        if user in votes[1]:
            votes[1].remove(user)
    votes = [len(val) for val in votes]
    seconds = 0
    caption = f'-                                      -\n' \
              f'⏳ Осталось: <b>15 с</b>\n' \
              f'-                                      -'

    if not ready_users.get(race_id, False):
        ready_users[race_id] = {user_id: 0}
    else:
        ready_users[race_id][user_id] = 0

    permissions[user_id] = 1
    for i in range(150):
        inline_keyboard = reply_markups[user_id]

        if i % 10 == 0:
            old_votes = votes
            votes = list(voting[race_id].values())
            for user in votes[0]:
                if user in votes[1]:
                    votes[1].remove(user)
            votes = [len(val) for val in votes]

            if votes != old_votes:
                print('ok')
                try:
                    voting_image_path = voting_images_2.get(race_id, False)
                    if not voting_image_path:
                        voting_image_path = [generate_circuit_choice_window(race_id, circuits_for_choice, votes)]
                        voting_images_2[race_id] = voting_image_path
                    elif len(voting_image_path) < sum(votes):
                        voting_image_path = [generate_circuit_choice_window(race_id, circuits_for_choice, votes)]
                        voting_images_2[race_id] += voting_image_path

                    media = InputMedia(media=InputFile(voting_image_path[-1]))

                    # try:
                    await message.edit_media(media, reply_markup=inline_keyboard)
                    # await message.edit_caption(caption, reply_markup=inline_keyboard)
                    # except:
                    #     photo = InputFile(voting_image_path[-1])
                    #     message = await bot.send_photo(user_id, photo, caption, reply_markup=inline_keyboard)

                except Exception as e:
                    print(e)

            seconds += 1

            caption = f'-                                      -\n' \
                      f'⏳ Осталось: <b>{15 - seconds} с</b>\n' \
                      f'-                                      -' \

            try:
                ...
                # await message.edit_caption(caption, reply_markup=inline_keyboard)
            except:
                voting_image_path = voting_images_2.get(race_id, False)
                if not voting_image_path:
                    voting_image_path = [generate_circuit_choice_window(race_id, circuits_for_choice, votes)]
                    voting_images_2[race_id] = voting_image_path
                elif len(voting_image_path) < sum(votes):
                    voting_image_path = [generate_circuit_choice_window(race_id, circuits_for_choice, votes)]
                    voting_images_2[race_id] += voting_image_path

                photo = InputFile(voting_image_path[-1])
                message = await bot.send_photo(user_id, photo, caption, reply_markup=inline_keyboard)

        await asyncio.sleep(0.1)

    ready_users[race_id][user_id] = 1
    while not (all(list(ready_users[race_id].values()))):
        await asyncio.sleep(0.1)

    await message.delete()
    msg = await message.answer("⏳ Загружаем данные гонки...")

    cur_circuit_id = cursor.execute("SELECT race_circuit FROM races WHERE id = ?", (race_id,)).fetchone()[0]
    if cur_circuit_id == -1:
        choosen_circuit = list(voting[race_id].keys())[0]
        for circuit_id in list(voting[race_id].keys()):
            if len(voting[race_id][circuit_id]) > len(voting[race_id][choosen_circuit]):
                choosen_circuit = circuit_id
            elif len(voting[race_id][circuit_id]) == len(voting[race_id][choosen_circuit]):
                choosen_circuit = random.choice([circuit_id, choosen_circuit])

        cursor.execute("UPDATE races SET race_circuit = ? WHERE id = ?", (choosen_circuit, race_id))
        connection.commit()

    await asyncio.sleep(3)
    await msg.delete()


def create_race_conditions(race_id):
    if_exists = bool(cursor.execute("SELECT weather FROM races WHERE id = ?", (race_id,)).fetchone()[0])
    if not if_exists:
        weather = ['sunny'] * 5 + ['cloudly'] * 5 + ['overcast'] * 3 + ['rain'] * 2 + ['shower'] * 1
        pitstops = -1
        laps = 3

        current_weather = random.choice(weather)

        cursor.execute("UPDATE races SET (weather, pitstops, laps) = (?, ?, ?) WHERE id = ?",
                       (current_weather, pitstops, laps, race_id))
        connection.commit()


async def show_race_info(user_id, race_id):
    create_race_conditions(race_id)

    info_window_path = generate_race_info_window(race_id)
    photo = InputFile(info_window_path)

    msg = await bot.send_photo(user_id, photo)
    await asyncio.sleep(4)
    await msg.delete()


tires = dict()
current_tires_index = dict()


async def choose_start_tires(user_id, race_id):
    global tires
    global current_tires_index

    user_cars = cursor.execute("SELECT car_1, car_2, car_3, car_4 FROM user_car_deck WHERE user_id = ?",
                               (user_id,)).fetchone()

    if not tires.get(race_id, False):
        tires[race_id] = dict()
    tires[race_id][user_id] = {key: ['', 100] for key in user_cars}
    tires_types = list(tires_characteristics.keys())

    index = 0
    for car_id in user_cars:
        msg_to_delete = await bot.send_message(user_id, "⏳ Загрузка...")

        car_tires = cursor.execute("SELECT * FROM user_tires_amount WHERE (user_id, car_id) = (?, ?)",
                                   (user_id, car_id)).fetchone()[2:]
        inds = []
        for i in range(len(car_tires)):
            if car_tires[i] != 0:
                inds.append(i)
                generate_tires_for_race_choice_window(race_id, user_id, index, i, tires[race_id][user_id])

        ind = inds[0]
        current_tires_index[user_id] = [inds[0], len(inds), 0]
        tires[race_id][user_id][car_id] = [tires_types[inds[ind]], 100]

        # photo_path = generate_tires_for_race_choice_window(race_id, user_id, user_cars.index(car_id), inds[ind],
        #                                                    tires[race_id][user_id])
        photo_path = os.path.join(f'images/for_saves/races/'
                                  f'{race_id}_{user_id}_{index}_{inds[ind]}_start-tires.png')
        photo = InputFile(photo_path)
        await msg_to_delete.delete()
        msg = await bot.send_photo(user_id, photo, reply_markup=RaceInlineKeyboard.start_tires_choice_menu)

        for i in range(12000):
            if ind != current_tires_index[user_id][0]:
                ind = current_tires_index[user_id][0]

                tires[race_id][user_id][car_id] = [tires_types[inds[ind]], 100]

                # photo_path = generate_tires_for_race_choice_window(race_id, user_id, user_cars.index(car_id), inds[ind],
                #                                                    tires[race_id][user_id])
                photo_path = os.path.join(f'images/for_saves/races/'
                                          f'{race_id}_{user_id}_{index}_{inds[ind]}_start-tires.png')
                photo = InputFile(photo_path)
                media = InputMedia(media=photo)

                msg = await bot.edit_message_media(media, user_id, msg.message_id,
                                                   reply_markup=RaceInlineKeyboard.start_tires_choice_menu)
                # msg = await bot.send_photo(user_id, photo, reply_markup=RaceInlineKeyboard.start_tires_choice_menu)

            elif current_tires_index[user_id][2] == 1:
                for j in range(len(inds)):
                    try:
                        os.remove(os.path.join(f'images/for_saves/races/'
                                               f'{race_id}_{user_id}_{index}_{inds[j]}_start-tires.png'))
                    except Exception as e:
                        print(e)

                await msg.delete()
                break

            await asyncio.sleep(0.1)

        index += 1


def generate_race_pictures(user_id, race_id):
    user_cars = cursor.execute("SELECT car_1, car_2, car_3, car_4 FROM user_car_deck WHERE user_id = ?",
                               (user_id,)).fetchone()
    for car_id in user_cars:
        car_tires = tires[race_id][user_id][car_id][0]
        save_path = os.path.join(f'images/for_saves/races/{race_id}_{user_id}_car{car_id}.png')
        generate_card_picture(user_id, car_id, path=save_path, tires=car_tires)


# async def play_circuit_race(users: list):
#     current_races = cursor.execute("SELECT id FROM races").fetchall()
#     if current_races is None:
#         race_id = 0
#     else:
#         race_id = current_races[-1][0] + 1
#
#     members = ' '.join([str(user) for user in users])
#
#     cursor.execute("INSERT INTO races VALUES (?, ?, ?, ?)", (race_id, 'circuit', members, 0))
#     connection.commit()


@dp.callback_query_handler(text_contains='подтверждение-гонки')
async def accept_race(call: CallbackQuery):
    await call.answer()

    user_id = call.from_user.id
    confirmation = int(call.data.split('_')[1])

    confirmations_id = get_service_data(user_id, 'race_confirmation_id')
    members_confirmations = cursor.execute("SELECT confirmations FROM race_confirmations WHERE id = ?",
                                           (confirmations_id,)).fetchone()[0]
    new_confirmations = ''
    for member_status in members_confirmations.split():
        if int(member_status.split('-')[0]) == user_id:
            new_confirmations += f'{user_id}-{confirmation} '
        else:
            new_confirmations += f'{member_status} '

    cursor.execute("UPDATE race_confirmations SET confirmations = ? WHERE id = ?",
                   (new_confirmations[:-1], confirmations_id))
    connection.commit()


@dp.callback_query_handler(text='отменить-поиск')
async def decline_search(call: CallbackQuery):
    await call.answer()

    user_id = call.from_user.id

    cursor.execute("UPDATE race_search SET race_type = ? WHERE user_id = ?", (-1, user_id))
    connection.commit()


@dp.callback_query_handler(text_contains='выбрать-трассу_')
async def choose_circuit(call: CallbackQuery):
    await call.answer()
    # try:
    #     await call.message.delete()
    # except:
    #     ...

    global permissions
    global voting
    global reply_markups

    user_id = call.from_user.id
    circuit_index = int(call.data.split('_')[1])
    race_id = get_service_data(user_id, 'race_confirmation_id')

    choosen_circuit = list(voting[race_id].keys())[circuit_index]

    voting[race_id][choosen_circuit].add(user_id)
    inline_keyboard = RaceInlineKeyboard.conf_menu_waiting

    reply_markups[user_id] = inline_keyboard


@dp.callback_query_handler(text_contains='стартовые-шины_')
async def start_tires_choice(call: CallbackQuery):
    await call.answer()

    global current_tires_index

    user_id = call.from_user.id
    direction = call.data.split('_')[1]
    current_index = current_tires_index[user_id][0]
    max_ind = current_tires_index[user_id][1] - 1
    if direction == 'вправо':
        current_index += 1
        if current_index > max_ind:
            current_index = 0
    elif direction == 'влево':
        current_index -= 1
        if current_index < 0:
            current_index = max_ind
    elif direction == 'выбрать':
        current_tires_index[user_id][2] = 1

    current_tires_index[user_id][0] = current_index


@dp.callback_query_handler(text='ожидание')
async def waiting_confirmation(call: CallbackQuery):
    await call.answer()
