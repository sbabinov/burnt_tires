import os
import random
import time

from PIL import Image, ImageDraw, ImageFont
from loader import cursor, connection
from objects_data import *
from .generate_car_pictures import *
from .generate_other_pictures import *


def generate_race_choice_window():
    # шрифты
    title_font, type_font, league_font = get_fonts('blogger_sans.ttf', 80, 70, 60)

    # фон
    background = Image.open('images/design/theme_5.jpg').convert(mode='RGBA')
    difference = 1000 / background.width
    background.resize((1000, int(background.height * 1.1 * difference)))
    idraw = ImageDraw.Draw(background)

    # заголовок
    title = 'Выберите режим:'
    text_width = idraw.textsize(title, font=title_font)[0]

    pos_x = (background.width - text_width) // 2
    pos_y = 50
    idraw.text((pos_x, pos_y), title, font=title_font, stroke_fill='black', stroke_width=10)

    # режимы
    circuit = Image.open('images/design/race_types/circuit.jpg').convert(mode='RGBA')
    circuit.thumbnail((900, 900))
    idraw_2 = ImageDraw.Draw(circuit)

    name = 'Трасса'
    league = 'Дивизион II'

    text_width = idraw_2.textsize(name, font=type_font)[0]
    pos_x = (circuit.width - text_width) // 2
    pos_y = 100
    idraw_2.text((pos_x, pos_y), name, font=title_font, stroke_fill='black', stroke_width=10)



    return circuit


def generate_race_map(circuit_id, page, laps):
    circuit_name = cursor.execute("SELECT name FROM race_circuits WHERE id = ?", (circuit_id,)).fetchone()[0]
    circuit_elements = cursor.execute("SELECT elements FROM race_circuits WHERE id = ?", (circuit_id,)).fetchone()[0]
    circuit_map = []
    for lap in range(laps):
        if lap != 0:
            circuit_map.append('10')
        for el in circuit_elements.split('_'):
            circuit_map.append(el)

    circuit_map = ['0'] + circuit_map + ['11']

    start_index = page * 15
    circuit_map = circuit_map[start_index:start_index + 15]

    # фон
    background = Image.open(os.path.join('images/design/theme_4.jpg')).convert(mode='RGBA')
    background.thumbnail((1000, 1000))
    background = background.resize((background.width, int(background.height * 1.2)))

    idraw = ImageDraw.Draw(background)

    # шрифты
    caption_font = get_fonts('blogger_sans.ttf', 30)[0]

    # элементы трассы
    arrow = Image.open(os.path.join(f'images/race_circuits/turns/arrow.png'))
    arrow.thumbnail((30, 30))
    reverse_arrow = arrow.rotate(-180, expand=True)
    down_arrow = arrow.rotate(-90, expand=True)

    pos_x = 35
    pos_y = 30

    reverse = False
    current_lap = 1
    for ind in range(len(circuit_map)):
        circuit_element_id = int(circuit_map[ind])
        circuit_element_name = elements_names[circuit_element_id]
        circuit_element_img = Image.open(os.path.join(f'images/race_circuits/turns/{circuit_element_id}.png'))
        circuit_element_img.thumbnail((130, 130))

        if circuit_element_id == 10:
            circuit_element_name = f'{current_lap} круг'
            current_lap += 1

        background.alpha_composite(circuit_element_img, (pos_x, pos_y))

        c_pos_y = pos_y + circuit_element_img.height + 10
        if ind == 0 and page != 0:
            background.alpha_composite(arrow, (pos_x - arrow.width - 10,
                                               pos_y + circuit_element_img.height // 2))

        for caption_part in circuit_element_name.split(' '):
            if circuit_element_id == 10:
                caption_part = circuit_element_name
            caption_width = idraw.textsize(caption_part, font=caption_font)[0]
            c_pos_x = pos_x + circuit_element_img.width // 2 - caption_width // 2
            idraw.text((c_pos_x, c_pos_y), caption_part, font=caption_font)
            c_pos_y += 20
            if circuit_element_id == 10:
                break

        if circuit_element_id == 11:
            break

        if len(circuit_element_name.split(' ')) > 1:
            down_arrow_pos_y = c_pos_y + 20
        else:
            down_arrow_pos_y = c_pos_y + 30
        if not reverse:
            if ind == 4:
                reverse = True
                background.alpha_composite(down_arrow, (pos_x + circuit_element_img.width // 2 - 15, down_arrow_pos_y))
                pos_y += 250
            else:
                if ind != len(circuit_elements) - 1:
                    background.alpha_composite(arrow, (pos_x + circuit_element_img.width + 10,
                                                       pos_y + circuit_element_img.height // 2))
                    pos_x += 200
        else:
            if ind in (9, 19):
                reverse = False
                background.alpha_composite(down_arrow, (pos_x + circuit_element_img.width // 2 - 15, down_arrow_pos_y))
                pos_y += 250
            else:
                background.alpha_composite(reverse_arrow, (pos_x - reverse_arrow.width - 20,
                                                           pos_y + circuit_element_img.height // 2))
                pos_x -= 200

    return background


def generate_scoring_window(user_id: int, car_dict: dict, circuit_element_id: int, dice: int, priority_dice: int):
    car_list = list(car_dict.keys())

    username = cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()[0]
    circuit_element_name = elements_names[circuit_element_id]

    # шрифты
    username_font, caption_font = get_fonts('blogger_sans.ttf', 40, 30)

    # фон
    background = Image.open('images/design/theme_4.jpg').convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(background)

    # линия посередине
    pos_x = background.width // 2
    pos_y = background.height - 30

    idraw.rectangle((pos_x, 30, pos_x + 3, pos_y), fill='white')

    # изображения карточек
    angles = [-5, 1, -3, 4, -2, 4]
    center_x = background.width // 4
    center_y = background.height // 2

    for ind in range(len(car_dict)):
        user_id = car_list[ind]
        car_id = car_dict[user_id]

        car_card_image = Image.open(generate_card_picture(user_id, car_id)).rotate(angles[ind], expand=True)
        car_card_image.thumbnail((500, 500))

        pos_x = center_x - car_card_image.width // 2
        pos_y = center_y - car_card_image.height // 2

        background.alpha_composite(car_card_image, (pos_x, pos_y))

    # значок элемента трассы и приоритетной грани кубика
    circuit_element_img = Image.open(os.path.join(f'images/race_circuits/turns/{circuit_element_id}.png'))
    circuit_element_img.thumbnail((130, 130))

    dice_img = Image.open(os.path.join(f'images/icons/dice/{dice}.png'))
    priority_dice_img = Image.open(os.path.join(f'images/icons/dice/{priority_dice}.png'))
    dice_img.thumbnail((100, 100))
    priority_dice_img.thumbnail((100, 100))

    el_pos_x = background.width - (3 * background.width // 8) - circuit_element_img.width // 2
    dice_pos_x = background.width - background.width // 8 - dice_img.width // 2
    el_pos_y = 150 - circuit_element_img.height
    dice_pos_y = 150 - dice_img.height

    background.alpha_composite(circuit_element_img, (el_pos_x, el_pos_y))
    background.alpha_composite(dice_img, (dice_pos_x, dice_pos_y))

    caption = 'Приоритет'
    pos_y = 170
    text_width = idraw.textsize(caption, font=caption_font)[0]
    pos_x = dice_pos_x + dice_img.width // 2 - text_width // 2
    idraw.text((pos_x, pos_y), caption, font=caption_font, stroke_fill='black', stroke_width=4)
    for name_part in circuit_element_name.split():
        text_width = idraw.textsize(name_part, font=caption_font)[0]
        pos_x = el_pos_x + circuit_element_img.width // 2 - text_width // 2
        idraw.text((pos_x, pos_y), name_part, font=caption_font, stroke_fill='black', stroke_width=4)
        pos_y += 30

    # юзернейм игрока
    pos_y = 250
    for caption_part in ('Ход игрока', username):
        text_width = idraw.textsize(caption_part, font=username_font)[0]
        pos_x = background.width - background.width // 4 - text_width // 2

        idraw.text((pos_x, pos_y), caption_part, font=username_font, stroke_fill='black', stroke_width=5)
        pos_y += 40


    return background

# generate_scoring_window(1005532278, {1005532278: 4}, 2, 2, 5).show()


async def generate_race_members_picture(race_id: int, page_index: int):
    members = cursor.execute("SELECT members FROM races WHERE id = ?", (race_id,)).fetchone()[0].split()
    sorted_members = [[]]
    for member in members:
        if len(sorted_members[-1]) < 2:
            sorted_members[-1].append(int(member))
        else:
            sorted_members.append([int(member)])

    # шрифты
    username_font, caption_font = get_fonts('blogger_sans.ttf', 40, 30)

    # фон
    background = Image.open('images/design/theme_4.jpg').convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(background)

    # линия посередине
    pos_x = background.width // 2
    pos_y = background.height - 30

    idraw.rectangle((pos_x, 30, pos_x + 3, pos_y), fill='white')

    # информация про участников
    pos_y = 30
    pos_x = 0
    for member_id in sorted_members[page_index]:
        username = cursor.execute("SELECT username FROM users WHERE id = ?", (member_id,)).fetchone()[0]
        # preview_car_id = cursor.execute("SELECT preview_car FROM user_car_deck WHERE user_id = ?",
        #                                 (member_id,)).fetchone()[0]
        # car_brand = cursor.execute("SELECT car_brand FROM cars WHERE id = ?", (preview_car_id,)).fetchone()[0]

        # имя пользователя
        text_width = idraw.textsize(username, font=username_font)[0]

        un_pos_x = pos_x + (background.width // 2 - text_width) // 2
        idraw.text((un_pos_x, pos_y), username, font=username_font, stroke_fill='black', stroke_width=5)

        # # изображение автомобиля
        # car_image = Image.open(os.path.join(f'images/cars/{car_brand}/{preview_car_id}.png'))
        # car_image.thumbnail((320, 320))
        avatar_image = await generate_user_profile_photo(member_id)
        avatar_image.thumbnail((280, 280))

        avr_pos_x = pos_x + (background.width // 2 - avatar_image.width) // 2
        background.alpha_composite(avatar_image, (avr_pos_x, 400 - avatar_image.height))

        # информация о пользователе
        info = {
            'Лига:': 'бронзовая',
            'Количество побед:': 4,
            'Стиль вождения:': 'аккуратный'
        }

        info_pos_y = 450
        for key in list(info.keys()):
            value = info[key]

            cur_pos_x = pos_x + 50
            for caption_part in (str(key), str(value)):
                if caption_part == 'аккуратный':
                    color = '#18D404'
                elif caption_part == 'агрессивный':
                    color = 'red'
                else:
                    color = 'white'

                text_width = idraw.textsize(caption_part, font=caption_font)[0]
                idraw.text((cur_pos_x, info_pos_y), caption_part, font=caption_font, fill=color,
                           stroke_fill='black', stroke_width=4)
                cur_pos_x += text_width + 15

            info_pos_y += 35

        pos_x += background.width // 2

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 10000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_confirmation_window(confirmation_id: int):
    members = cursor.execute("SELECT confirmations FROM race_confirmations WHERE id = ?",
                             (confirmation_id,)).fetchone()[0]

    # шрифты
    title_font, caption_font = get_fonts('blogger_sans.ttf', 60, 40)

    # фон
    background = Image.open('images/design/theme_4.jpg').convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(background)

    # изображение галочки
    checkbox = Image.open(os.path.join('images/icons/checkbox.png'))
    checkbox.thumbnail((40, 40))

    # заголовок
    title = 'Участники гонки:'
    text_width = idraw.textsize(title, font=title_font)[0]

    idraw.text(((background.width - text_width) // 2, 40), title, font=title_font, stroke_fill='black', stroke_width=5)

    pos_y = 150
    for member in members.split():
        member_id = int(member.split('-')[0])
        member_status = int(member.split('-')[1])
        member_username = cursor.execute("SELECT username FROM users WHERE id = ?", (member_id,)).fetchone()[0]

        text_width, text_height = idraw.textsize(member_username, font=caption_font)
        pos_x = (background.width - text_width) // 2
        idraw.text((pos_x, pos_y), member_username, font=caption_font, stroke_fill='black', stroke_width=4)

        if member_status == 1:
            background.alpha_composite(checkbox,
                                       (pos_x + text_width + 15, pos_y + text_height // 2 - checkbox.height // 2))
        pos_y += 50

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 1000000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_circuit_choice_window(circuit_ids: tuple | list, voices: tuple | list = (0, 0)):
    # шрифты
    title_font, name_font, caption_font = get_fonts('blogger_sans.ttf', 55, 35, 40)

    # фон
    background = Image.open('images/design/theme_4.jpg').convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(background)

    # заголовок
    title = 'Проголосуйте за трассу:'
    text_width = idraw.textsize(title, font=title_font)[0]

    pos_x = (background.width - text_width) // 2
    pos_y = 30

    idraw.text((pos_x, pos_y), title, font=title_font, stroke_fill='black', stroke_width=5)

    # линия посередине
    pos_x = background.width // 2
    pos_y = background.height - 30

    idraw.rectangle((pos_x, 120, pos_x + 3, pos_y), fill='white')

    # информация о трассах
    circuits_height = []
    for circuit_id in circuit_ids:
        circuit_image = Image.open(os.path.join(f'images/race_circuits/{circuit_id}.png')).convert(mode='RGBA')
        circuit_image.thumbnail((400, 300))

        circuits_height.append(circuit_image.height)

    pos_x = 0
    ind = 0
    for circuit_id in circuit_ids:
        circuit_image = Image.open(os.path.join(f'images/race_circuits/{circuit_id}.png')).convert(mode='RGBA')
        circuit_image.thumbnail((400, 300))

        # изображение трассы
        circ_pos_y = 130 + max(circuits_height) - circuit_image.height
        circ_pos_x = pos_x + (background.width // 2 - circuit_image.width) // 2

        background.alpha_composite(circuit_image, (circ_pos_x, circ_pos_y))

        # название трассы
        circuit_name = cursor.execute("SELECT name FROM race_circuits WHERE id = ?", (circuit_id,)).fetchone()[0]

        text_width = idraw.textsize(circuit_name, font=name_font)[0]
        name_pos_x = pos_x + (background.width // 2 - text_width) // 2
        name_pos_y = circ_pos_y + circuit_image.height + 30

        idraw.text((name_pos_x, name_pos_y), circuit_name, font=name_font,
                   stroke_fill='black', stroke_width=4)

        # голоса
        caption = f'Голосов: {voices[ind]}'
        text_width = idraw.textsize(caption, font=caption_font)[0]
        cap_pos_x = pos_x + (background.width // 2 - text_width) // 2
        cap_pos_y = name_pos_y + 65

        idraw.text((cap_pos_x, cap_pos_y), caption, font=caption_font, fill='yellow',
                   stroke_fill='black', stroke_width=5)

        pos_x += background.width // 2
        ind += 1

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 1000000000)}.png')
    background.save(save_path)
    background.close()

    return save_path





