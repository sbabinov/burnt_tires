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


def generate_race_map(race_id, user_id, page, laps, open_elements):
    circuit_id = cursor.execute("SELECT race_circuit FROM races WHERE id = ?", (race_id,)).fetchone()[0]
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

        if ind + 1 == open_elements:
            break

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 10000000000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_scoring_window(race_id: int, user_id: int, car_id: int, tires: str, circuit_element_id: int, dice: int,
                            priority_dice: int, characteristics_bonus: int, dice_bonus: int, event_bonus: int):

    username = cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()[0]
    circuit_element_name = elements_names[circuit_element_id]

    # шрифты
    username_font, caption_font = get_fonts('blogger_sans.ttf', 40, 30)
    score_font, score_font_small = get_fonts('Drina.ttf', 60, 40)

    # фон
    background = Image.open('images/design/theme_4.jpg').convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(background)

    # линия посередине
    pos_x = background.width // 2
    pos_y = background.height - 30

    idraw.rectangle((pos_x, 30, pos_x + 3, pos_y), fill='white')

    # значок шин
    tires_logo = Image.open(os.path.join(f'images/cars_parts/tires/logos/{tires}.png')).convert(mode='RGBA')
    tires_logo.thumbnail((100, 100))

    # изображения карточек
    angle = random.randint(-4, 4)
    center_x = background.width // 4
    center_y = background.height // 2

    save_path = f'images/for_saves/races/{race_id}_{user_id}_car{car_id}.png'
    car_card_image = Image.open(save_path)
    car_card_image.alpha_composite(tires_logo, (car_card_image.width - tires_logo.width - 30,
                                                car_card_image.height - tires_logo.height - 30))
    car_card_image = car_card_image.rotate(angle, expand=True)
    car_card_image.thumbnail((550, 550))

    pos_x = center_x - car_card_image.width // 2
    pos_y = center_y - car_card_image.height // 2

    background.alpha_composite(car_card_image, (pos_x, pos_y))

    # значок элемента трассы и приоритетной грани кубика
    circuit_element_img = Image.open(os.path.join(f'images/race_circuits/turns/{circuit_element_id}.png'))
    circuit_element_img.thumbnail((130, 130))

    dice_img = Image.open(os.path.join(f'images/icons/dice/{dice}.png'))
    priority_dice_img = Image.open(os.path.join(f'images/icons/dice/{priority_dice}.png'))
    dice_img.thumbnail((50, 50))
    priority_dice_img.thumbnail((100, 100))

    el_pos_x = background.width - (3 * background.width // 8) - circuit_element_img.width // 2
    dice_pos_x = background.width - background.width // 8 - priority_dice_img.width // 2
    el_pos_y = 150 - circuit_element_img.height
    dice_pos_y = 150 - priority_dice_img.height

    background.alpha_composite(circuit_element_img, (el_pos_x, el_pos_y))
    background.alpha_composite(priority_dice_img, (dice_pos_x, dice_pos_y))

    caption = 'Приоритет'
    pos_y = 170
    text_width = idraw.textsize(caption, font=caption_font)[0]
    pos_x = dice_pos_x + priority_dice_img.width // 2 - text_width // 2
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

    # бонусы
    pos_x = background.width // 2 + 30
    pos_y = pos_y + 40

    caption = 'Выпало:'
    text_width = idraw.textsize(caption, font=caption_font)[0]
    idraw.text((pos_x, pos_y), caption, font=caption_font, stroke_width=4, stroke_fill='black')
    background.alpha_composite(dice_img, (pos_x + text_width + 20, pos_y - 15))

    captions = ['Характеристики:', 'Бонус кубика:', 'Бонус события:']
    values = [characteristics_bonus, dice_bonus, event_bonus]
    for index in range(len(captions)):
        caption = captions[index]
        value = values[index]
        if index == 0:
            value = f'{value} очк.'
            color = '#30BD03'
        else:
            if value < 1:
                color = 'red'
            elif value == 1:
                color = 'white'
                value = '-'
            else:
                color = '#30BD03'
            value = f'x{value}' if value != '-' else '-'

        pos_y += 50
        text_width = idraw.textsize(caption, font=caption_font)[0]
        idraw.text((pos_x, pos_y), caption, font=caption_font, stroke_width=4, stroke_fill='black')
        idraw.text((pos_x + text_width + 20, pos_y - 20), value, font=score_font,
                   fill=color)

    # сумма очков
    line_image = Image.open(os.path.join('images/icons/line.png')).convert(mode='RGBA').rotate(45, expand=True)
    line_image.thumbnail((150, 150))

    pos_x = background.width - line_image.width - 30
    pos_y = background.height - line_image.height - 30

    background.alpha_composite(line_image, (pos_x, pos_y))

    score = int(characteristics_bonus * dice_bonus * event_bonus)
    text_width = idraw.textsize(str(score), font=score_font)[0]
    pos_x = background.width - 50 - text_width // 2
    pos_y += 50

    idraw.text((pos_x, pos_y), str(score), font=score_font, fill='#FFE500')
    idraw.text((920, pos_y + 50), 'очк.', font=score_font_small, fill='#FFE500')

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 100000000000)}.png')
    background.save(save_path)
    background.close()
    #
    return save_path
    # return background

# generate_scoring_window(64, 1005532278, 1, 'hard', 2, 2, 5).show()


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

        # имя пользователя
        text_width = idraw.textsize(username, font=username_font)[0]

        un_pos_x = pos_x + (background.width // 2 - text_width) // 2
        idraw.text((un_pos_x, pos_y), username, font=username_font, stroke_fill='black', stroke_width=5)

        # аватарка
        avatar_image = await generate_user_profile_photo(member_id)
        avatar_image.thumbnail((280, 280))

        path = os.path.join(f'images/for_saves/races/profile_{member_id}.png')
        avatar_image.save(path)

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

    save_path = os.path.join(f'images/for_saves/races/{race_id}.png')
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


def generate_circuit_choice_window(race_id, circuit_ids: tuple | list, voices: tuple | list = (0, 0)):
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
        circuit_image = \
            Image.open(os.path.join(f'images/race_circuits/{circuit_id}/{circuit_id}.png')).convert(mode='RGBA')
        circuit_image.thumbnail((400, 300))

        circuits_height.append(circuit_image.height)

    pos_x = 0
    ind = 0
    for circuit_id in circuit_ids:
        circuit_image = \
            Image.open(os.path.join(f'images/race_circuits/{circuit_id}/{circuit_id}.png')).convert(mode='RGBA')
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

    save_path = os.path.join(f'images/for_saves/races/{race_id}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_race_info_window(race_id):
    weather = cursor.execute("SELECT weather FROM races WHERE id = ?", (race_id,)).fetchone()[0]
    pitstop = cursor.execute("SELECT pitstops FROM races WHERE id = ?", (race_id,)).fetchone()[0]
    circuit_id = cursor.execute("SELECT race_circuit FROM races WHERE id = ?", (race_id,)).fetchone()[0]
    laps = cursor.execute("SELECT laps FROM races WHERE id = ?", (race_id,)).fetchone()[0]

    # шрифты
    title_font, caption_font, laps_font = get_fonts('blogger_sans.ttf', 60, 35, 50)

    # фон
    background = Image.open('images/design/theme_4.jpg').convert(mode='RGBA')
    background.thumbnail((1000, 1000))
    background = background.resize((background.width, int(background.width * 45 / 64)))

    idraw = ImageDraw.Draw(background)

    # заголовок
    title = 'Информация о гонке:'
    text_width = idraw.textsize(title, font=title_font)[0]

    pos_x = (background.width - text_width) // 2
    idraw.text((pos_x, 35), title, font=title_font, stroke_fill='black', stroke_width=5)

    # изображение трассы
    circuit_name = cursor.execute("SELECT name FROM race_circuits WHERE id = ?", (circuit_id, )).fetchone()[0]
    circuit_image = Image.open(os.path.join(f'images/race_circuits/{circuit_id}/{circuit_id}.png')).convert(mode='RGBA')
    circuit_image.thumbnail((450, 350))

    laps_caption = f'Кругов: {laps}'

    name_text_size = idraw.textsize(circuit_name, font=caption_font)
    laps_text_size = idraw.textsize(laps_caption, font=laps_font)

    pos_x = int(background.width * 0.6 - circuit_image.width) // 2
    pos_y = 70 + (background.height - circuit_image.height - 50 - laps_text_size[1] -
                  name_text_size[1] - 20 - 60) // 2

    background.alpha_composite(circuit_image, (pos_x, pos_y))

    # название трассы
    name_pos_x = pos_x + (circuit_image.width - name_text_size[0]) // 2
    name_pos_y = pos_y + circuit_image.height + 20

    idraw.text((name_pos_x, name_pos_y), circuit_name, font=caption_font)

    # количество кругов
    pos_x = pos_x + (circuit_image.width - laps_text_size[0]) // 2
    pos_y = name_pos_y + name_text_size[1] + 60

    idraw.text((pos_x, pos_y), laps_caption, font=laps_font, stroke_fill='black', stroke_width=4)

    # погода на старте
    idraw.text((630, 200), 'Погода', font=caption_font, stroke_fill='black', stroke_width=4)
    idraw.text((610, 240), 'на старте:', font=caption_font, stroke_fill='black', stroke_width=4)

    weather_image = Image.open(os.path.join(f'images/icons/weather/{weather}.png')).convert(mode='RGBA')
    weather_image.thumbnail((100, 100))

    background.alpha_composite(weather_image, (790, 230 - weather_image.height // 2))

    # пит-стоп
    if pitstop == -1:
        pitstop_caption = 'Без|ограничений'
        color = '#30BD03'
    else:
        color = 'yellow'
        if pitstop == 1:
            caption_part = 'обязательный|пит-стоп'
        else:
            caption_part = 'обязательных|пит-стопа'

        pitstop_caption = f'{pitstop} {caption_part}'

    pitstop_image = Image.open(os.path.join('images/icons/pitstop.png')).convert(mode='RGBA')
    pitstop_image.thumbnail((100, 100))

    pos_x = 590
    pos_y = 230 + weather_image.height // 2 + 40

    background.alpha_composite(pitstop_image, (pos_x, pos_y))

    pos_y = 230 + weather_image.height // 2 + 40 + 20
    for caption_part in pitstop_caption.split('|'):
        text_width = idraw.textsize(caption_part, font=caption_font)[0]

        text_width_1 = idraw.textsize(pitstop_caption.split('|')[0], font=caption_font)[0]
        text_width_2 = idraw.textsize(pitstop_caption.split('|')[1], font=caption_font)[0]
        c_pos_x = pos_x + pitstop_image.width + 20 + max(text_width_1, text_width_2) // 2 - text_width // 2

        idraw.text((c_pos_x, pos_y), caption_part, font=caption_font, fill=color, stroke_fill='black', stroke_width=5)
        pos_y += 30

    save_path = os.path.join(f'images/for_saves/races/{race_id}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_tires_for_race_choice_window(race_id, user_id, car_index, tires_index, tires):
    user_cars = cursor.execute("SELECT car_1, car_2, car_3, car_4 FROM user_car_deck WHERE user_id = ?",
                               (user_id,)).fetchone()

    # шрифты
    title_font, caption_font = get_fonts('blogger_sans.ttf', 50, 35)

    # фон
    background = Image.open('images/design/theme_6.jpg').convert(mode='RGBA')
    background.thumbnail((1000, 1000))
    background = background.resize((background.width, int(background.width * 45 / 64)))

    idraw = ImageDraw.Draw(background)

    # заголовок
    title = 'Выберите стартовый|комплект шин:'
    pos_y = 30
    for title_part in title.split('|'):
        text_width = idraw.textsize(title_part, font=title_font)[0]
        pos_x = (background.width - text_width) // 2
        idraw.text((pos_x, pos_y), title_part, font=title_font, stroke_fill='black', stroke_width=5)
        pos_y += 50

    # разграничительная линия
    line_pos_x = int(background.width * 0.58)
    pos_y_1 = pos_y + 40
    pos_y_2 = background.height - 50
    idraw.rectangle((line_pos_x, pos_y_1, line_pos_x + 2, pos_y_2), fill='white')

    # шины
    tires_names = list(tires_characteristics.keys())
    user_tires = cursor.execute("SELECT * FROM user_tires_amount WHERE (user_id, car_id) = (?, ?)",
                           (user_id, user_cars[car_index])).fetchone()[2:]
    current_tires_amount = user_tires[tires_index]

    tires_image = \
        Image.open(os.path.join(f'images/cars_parts/tires/{tires_names[tires_index]}.png')).convert(mode='RGBA')
    tires_image.thumbnail((220, 220))

    tires_logo = \
        Image.open(os.path.join(f'images/cars_parts/tires/logos/{tires_names[tires_index]}.png')).convert(mode='RGBA')
    tires_logo.thumbnail((100, 100))

    pos_x_1 = line_pos_x + 105
    pos_x_2 = background.width - 105 - tires_image.width
    pos_y_1 = 350 - tires_logo.height // 2
    pos_y_2 = 350 - tires_image.height // 2

    background.alpha_composite(tires_image, (pos_x_2, pos_y_2))
    background.alpha_composite(tires_logo, (pos_x_1, pos_y_1))

    tires_types = ['Мягкие', 'Средние', 'Жёсткие', 'Дождевые', 'Раллийные', 'Для бездорожья', 'Драговые']
    caption = f'{tires_types[tires_index]} (x{current_tires_amount})'
    text_width = idraw.textsize(caption, font=caption_font)[0]

    pos_x = line_pos_x + (background.width - line_pos_x) // 2 - text_width // 2
    pos_y = 520

    idraw.text((pos_x, pos_y), caption, font=caption_font, stroke_fill='black', stroke_width=4)

    # изображения автомобилей
    ind = 0
    processed_images = []
    for car_id in user_cars:
        brand_id = cursor.execute("SELECT car_brand FROM cars WHERE id = ?", (car_id,)).fetchone()[0]

        car_image = Image.open(os.path.join(f'images/cars/{brand_id}/{car_id}.png')).convert(mode='RGBA')
        car_image.thumbnail((230, 230))

        if car_index != ind:
            new_image = []
            for pixel in car_image.getdata():
                new_image.append((255, 255, 255, pixel[-1]))

            newim = Image.new(car_image.mode, car_image.size)
            newim.putdata(new_image)
            processed_images.append(newim)
        else:
            processed_images.append(car_image)

        ind += 1

    center_pos_x = 170
    bottom_pos_y = 350

    ind = 0
    for car_image in processed_images:
        pos_x = center_pos_x - car_image.width // 2
        pos_y = bottom_pos_y - car_image.height

        background.alpha_composite(car_image, (pos_x, pos_y))

        center_pos_x += 250
        if center_pos_x > 500:
            center_pos_x = 170
            bottom_pos_y += 220

        ind += 1

    # установленные комплекты шин
    center_pos_x = 170
    bottom_pos_y = 350

    for i in range(4):
        if car_index > i:
            tires_type = tires[user_cars[i]][0]
            tires_logo = \
                Image.open(os.path.join(f'images/cars_parts/tires/logos/{tires_type}.png')).convert(
                    mode='RGBA')
            tires_logo.thumbnail((90, 90))

            pos_x = center_pos_x - tires_logo.width // 2
            pos_y = bottom_pos_y - tires_logo.height - 10

            background.alpha_composite(tires_logo, (pos_x, pos_y))

            center_pos_x += 250
            if center_pos_x > 500:
                center_pos_x = 170
                bottom_pos_y += 220

    # боковые стрелки
    arrow = Image.open(os.path.join('images/icons/side_arrow.png')).convert(mode='RGBA')
    arrow = arrow.resize((int(arrow.width * 0.8), arrow.height))
    arrow.thumbnail((100, 100))
    reversed_arrow = arrow.rotate(180, expand=True)

    pos_x_1 = line_pos_x + 30
    pos_x_2 = background.width - 30 - arrow.width
    pos_y = 350 - arrow.height // 2

    background.alpha_composite(reversed_arrow, (pos_x_1, pos_y))
    background.alpha_composite(arrow, (pos_x_2, pos_y))

    save_path = os.path.join(f'images/for_saves/races/'
                             f'{race_id}_{user_id}_{car_index}_{tires_index}_start-tires.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_overtaking_window(data: dict):
    # шрифты
    caption_font = get_fonts('boycott.ttf', 140)[0]

    # фон
    background = Image.open('images/design/theme_6.jpg').convert(mode='RGBA')
    background.thumbnail((1000, 1000))
    # background = background.resize((background.width, int(background.width * 45 / 64)))

    idraw = ImageDraw.Draw(background)

    # надпись VS
    caption = 'VS'
    text_size = idraw.textsize(caption, font=caption_font)

    pos_x = (background.width - text_size[0]) // 2 + 15
    pos_y = (background.height - text_size[1]) // 2

    idraw.text((pos_x, pos_y), caption, font=caption_font)

    # автомобиль и аватарка первого пользователя
    center_x = (background.width // 2 - text_size[0] // 2) // 2 + 7
    center_y = 200
    for i in range(2):
        user_id, car_id = list(data.items())[i]
        car_brand = cursor.execute("SELECT car_brand FROM cars WHERE id = ?", (car_id,)).fetchone()[0]

        car_1_image = Image.open(os.path.join(f'images/cars/{car_brand}/{car_id}.png')).convert(mode='RGBA')
        car_1_image.thumbnail((320, 320))
        if i == 0:
            car_1_image = car_1_image.transpose(Image.FLIP_LEFT_RIGHT)

        pos_x = center_x - car_1_image.width // 2
        pos_y = center_y - car_1_image.height // 2

        background.alpha_composite(car_1_image, (pos_x, pos_y))

        if i == 0:
            center_y += 250
        else:
            center_y -= 250

        avatar = Image.open(os.path.join(f'images/for_saves/races/profile_{user_id}.png')).convert(mode='RGBA')
        avatar.thumbnail((200, 200))

        pos_x = center_x - avatar.width // 2
        pos_y = center_y - avatar.height // 2

        background.alpha_composite(avatar, (pos_x, pos_y))

        center_x = background.width // 2 + (background.width // 2 + text_size[0] // 2) // 2

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 100000000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


# generate_overtaking_window({1: 4, 2: 3}).show()
#
# generate_tires_for_race_choice_window(1005532278, tires_index=1).show()