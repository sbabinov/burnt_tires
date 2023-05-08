import os.path
import asyncio

from aiogram.types import InputFile, CallbackQuery, InputMedia, Message

from loader import dp, bot, update_current_message_id, update_service_data, get_service_data
from inline_keyboards import RaceInlineKeyboard
from useful_function.generate_race_pictures import *
from useful_function.generate_other_pictures import *


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
    members_confirmations = cursor.execute("SELECT confirmations FROM race_confirmations WHERE id = ?",
                                           (confirmations_id,)).fetchone()[0]

    image_path = generate_confirmation_window(confirmations_id)
    photo = InputFile(image_path)

    inline_keyboard = RaceInlineKeyboard.conf_menu_accept

    msg = await bot.send_photo(user_id, photo, reply_markup=inline_keyboard)

    os.remove(image_path)
    update_current_message_id(user_id, msg.message_id)
    stop = False
    for i in range(15):
        old_members_confirmations = members_confirmations
        members_confirmations = cursor.execute("SELECT confirmations FROM race_confirmations WHERE id = ?",
                                               (confirmations_id,)).fetchone()[0]

        for member in members_confirmations.split():
            member_id = int(member.split('-')[0])
            member_status = int(member.split('-')[1])

            if member_id == user_id and member_status == 1:
                inline_keyboard = RaceInlineKeyboard.conf_menu_waiting
                stop = True
                break

        if stop:
            break

        if old_members_confirmations != members_confirmations:
            try:
                image_path = generate_confirmation_window(confirmations_id)
                media = InputMedia(media=InputFile(image_path))

                msg = await bot.edit_message_media(media, user_id, msg.message_id,
                                                   reply_markup=inline_keyboard)
                os.remove(image_path)
            except:
                ...

        await asyncio.sleep(1)

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

        await asyncio.sleep(1)

    # занесение новой гонки в БД
    if permission:
        members = ' '.join([str(member) for member in sorted(members_list)])

        race_id = cursor.execute("SELECT race_id FROM race_confirmations WHERE id = ?", (confirmations_id,)).fetchone()[0]
        if not race_id:
            current_races = cursor.execute("SELECT id FROM races").fetchall()
            if current_races is None:
                race_id = 1
            else:
                race_id = current_races[-1][0] + 1

            cursor.execute("UPDATE race_confirmations SET race_id = ? WHERE id = ?", (race_id, confirmations_id))
            cursor.execute("INSERT INTO races VALUES (?, ?, ?, ?)", (race_id, 'circuit', members, 0))
            connection.commit()

        await msg.delete()

        return race_id

    return False


async def show_race_members(user_id: int, race_id: int):
    first_members_image_path = await generate_race_members_picture(race_id, 0)
    race_members = get_race_members(race_id)

    image = InputFile(first_members_image_path)

    msg = await bot.send_photo(user_id, image)
    os.remove(first_members_image_path)

    if len(race_members) > 2:
        for page_index in range(1, len(race_members) // 2 + (1 if len(race_members) % 2 != 0 else 0)):
            await asyncio.sleep(4)
            first_members_image_path = await generate_race_members_picture(race_id, page_index)
            image = InputFile(first_members_image_path)

            await msg.delete()
            msg = await bot.send_photo(user_id, image)
            os.remove(first_members_image_path)

    await msg.delete()


async def circuit_voting(user_id):
    circuits_for_choice = []
    circuit_ids = [circ[0] for circ in cursor.execute("SELECT id FROM race_circuits").fetchall()]
    for _ in range(2):
        circuit_id = random.choice(circuit_ids)
        circuit_ids.remove(circuit_id)
        circuits_for_choice.append(circuit_id)

    image_path = generate_circuit_choice_window(circuits_for_choice)
    image = InputFile(image_path)

    await bot.send_photo(user_id, image)
    os.remove(image_path)


async def play_circuit_race(users: list):
    current_races = cursor.execute("SELECT id FROM races").fetchall()
    if current_races is None:
        race_id = 0
    else:
        race_id = current_races[-1][0] + 1

    members = ' '.join([str(user) for user in users])
    # users_cars = {}
    # for user_id in users:
    #     user_cars = cursor.execute("SELECT * FROM user_car_deck WHERE user_id = ?", (user_id,)).fetchone()[1:]
    #     users_cars[user_id] = user_cars
    #
    #     members += f'{user_id} '

    cursor.execute("INSERT INTO races VALUES (?, ?, ?, ?)", (race_id, 'circuit', members, 0))
    connection.commit()





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
        race_id = await game_confirmation(user_id, conf_id)
        if race_id:
            await show_race_members(user_id, race_id)
            await circuit_voting(user_id)


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


@dp.callback_query_handler(text='ожидание')
async def waiting_confirmation(call: CallbackQuery):
    await call.answer()



