import os
import random
import time

from PIL import Image, ImageDraw, ImageFont
from loader import cursor, connection
from objects_data import *
from useful_function import calculate_characteristic_bar_length


def get_fonts(font: str, *sizes):
    font_path = os.path.join(f'fonts/{font}')
    fonts = []
    for size in sizes:
        font = ImageFont.truetype(font_path, size=size)
        fonts.append(font)
    return fonts


def get_displayed_price(price: int):
    caption = '$'
    bit_counter = 0
    for str_index in range(len(str(price)) - 1, -1, -1):
        if bit_counter % 3 == 0 and bit_counter != 0:
            caption = ' ' + caption
        caption = str(price)[str_index] + caption
        bit_counter += 1

    return caption


def generate_album_photo(user_id, brand_id: int, cars: list, choose_car_index: int, fast_load=False):
    brand = cars_brands[brand_id]
    car_country = 'Italia'

    if not fast_load:
        # фон
        background = Image.open(os.path.join('images/design/theme.jpg')).convert(mode='RGBA')
        background.thumbnail((1000, 1000))
        background = background.resize((1000, int(background.height * 1.1)))

        idraw = ImageDraw.Draw(background)

        # настройка шрифта
        font = os.path.join('fonts/blogger_sans.ttf')

        header_font = ImageFont.truetype(font, size=65)
        caption_font = ImageFont.truetype(font, size=30)

        # изображение бренда
        brand_image = Image.open(os.path.join(f'images/cars/{brand_id}/logo.png')).convert(mode='RGBA')
        brand_image.thumbnail((80, 80))

        # обработка автомобилей
        processed_images = []
        opened_car_ids = \
            [i[0] for i in cursor.execute("SELECT car_id FROM users_cars WHERE user_id = ?", (user_id,)).fetchall()]
        c = 0
        for car_id in cars:
            car_image = Image.open(os.path.join(f'images/cars/{brand_id}/{car_id}.png')).convert(mode='RGBA')
            car_image.thumbnail((200, 200))

            if car_id not in opened_car_ids:
                new_image = []
                for pixel in car_image.getdata():
                    new_image.append((255, 255, 255, pixel[-1]))

                newim = Image.new(car_image.mode, car_image.size)
                newim.putdata(new_image)
                processed_images.append(newim)
            else:
                processed_images.append(car_image)

            c += 1

        # добавление названия бренда
        pos_x = (background.width - (len(brand) * 35)) // 2 + (brand_image.width + 20) // 2
        idraw.text((pos_x, 40), brand, font=header_font)

        # добавление изображения бренда
        pos_y = 66 - brand_image.height // 2
        background.alpha_composite(brand_image, (pos_x - brand_image.width - 20, pos_y))

        # дообавление флага
        flag_image = Image.open(os.path.join(f'images/flags/{car_country}.png')).convert(mode='RGBA')
        flag_image.thumbnail((300, 300))

        flag_image = flag_image.rotate(45, expand=True)
        background.alpha_composite(flag_image, (800, -50))

        # добавление автомобилей
        max_height = max(processed_images[0].height, processed_images[1].height, processed_images[2].height)

        pos_x = 250
        pos_y = ((background.height - 60) - (max_height + 180 * 2 + 10)) // 2 + 60 + max_height
        index = 0
        rectangle_positions = []
        for car_image in processed_images:
            background.alpha_composite(car_image, (pos_x - car_image.width // 2, pos_y - car_image.height))

            caption = cursor.execute("SELECT car_model FROM cars WHERE id = ?", (cars[index],)).fetchone()[0]

            caption_pos_x = pos_x - (len(caption) * 14) // 2
            caption_pos_y = pos_y + 10

            idraw.text((caption_pos_x, caption_pos_y), caption, font=caption_font)

            x_1 = pos_x - car_image.width // 2 - 10
            y_1 = pos_y - car_image.height - 20
            x_2 = x_1 + car_image.width + 20
            y_2 = caption_pos_y + 35

            rectangle_positions.append((x_1, y_1, x_2, y_2))
            # idraw.rounded_rectangle((x_1, y_1, x_2, y_2), radius=10, fill=None, width=3)

            pos_x += 250
            if pos_x > 900:
                pos_x = 250
                pos_y += 180

            index += 1
        for file in os.listdir(os.path.join(f'images/for_saves/{user_id}')):
            if file.startswith('01'):
                os.remove(os.path.join(f'images/for_saves/{user_id}/{file}'))
        save_path = os.path.join(f'images/for_saves/{user_id}/'
                                 f'01_{"_".join([str(i[j]) for i in rectangle_positions for j in range(len(i))])}.png')
        background.save(save_path)

        idraw.rounded_rectangle(rectangle_positions[choose_car_index], radius=10, fill=None, width=3)
    else:
        for file in os.listdir(os.path.join(f'images/for_saves/{user_id}')):
            if file.startswith('01'):
                file_name = file
                break
        background = Image.open(os.path.join(f'images/for_saves/{user_id}/{file_name}'))
        idraw = ImageDraw.Draw(background)

        rectangle_positions = file_name.split('.')[0].split('_')[1:]
        for index in range(len(rectangle_positions) // 4):
            if choose_car_index == index:
                rectangle_positions = tuple(map(int, rectangle_positions[index * 4: index * 4 + 4]))
                idraw.rounded_rectangle(rectangle_positions, radius=10, fill=None, width=3)

    save_path = os.path.join(f'images/for_saves/{user_id}/{random.randint(100, 10000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_car_state_picture(user_id, car_id, size):
    data = cursor.execute("SELECT * FROM cars_body_state WHERE (user_id, car_id) = (?, ?)",
                          (user_id, car_id)).fetchone()[2:]
    body_parts = ['front', 'rear', 'roof', 'right_side', 'left_side']

    main_image = Image.open(os.path.join(f'images/car_states/body/full.png')).convert(mode='RGBA')
    main_image.thumbnail((size, size))

    for part_index in range(len(body_parts)):
        part_state = data[part_index]
        if part_state > 20:
            part_state = part_state - 20
        if part_state < 90:
            part_image = \
                Image.open(os.path.join(f'images/car_states/body/{body_parts[part_index]}.png')).convert(mode='RGBA')
            part_image.thumbnail((size, size))

            default_color_value = [255, 0]
            for i in range(part_state):
                if default_color_value[1] >= 255:
                    default_color_value[0] -= 255 / 50
                else:
                    default_color_value[1] += 255 / 50

            color = [int(default_color_value[0]), int(default_color_value[1]), 0, 255]
            if part_state == 0:
                color = [0, 0, 0, 255]

            new_image = []
            for pixel in part_image.getdata():
                if pixel[-1] > 0:
                    color = list(color)
                    color[-1] = pixel[-1]
                    color = tuple(color)
                    new_image.append(color)
                else:
                    new_image.append((0, 0, 0, 0))

            part_image = Image.new(part_image.mode, part_image.size)
            part_image.putdata(new_image)

            main_image.alpha_composite(part_image)

    return main_image


def generate_card_picture(user_id, car_id, backside=False, path=None, tires=None):
    # информация об автомобиле
    car_brand_id = cursor.execute("SELECT car_brand FROM cars WHERE id = ?", (car_id,)).fetchone()[0]
    car_brand = cars_brands[car_brand_id]

    car_model = cursor.execute("SELECT car_model FROM cars WHERE id = ?", (car_id,)).fetchone()[0]
    car_rarity = cursor.execute("SELECT rarity FROM cars WHERE id = ?", (car_id,)).fetchone()[0]

    improvements = cursor.execute("SELECT * FROM users_cars WHERE (user_id, car_id) = (?, ?)",
                                  (user_id, car_id)).fetchone()[2:-1]
    identified_improvements = []
    for ind in range(len(improvements)):
        if improvements[ind] == 1:
            identified_improvements.append(ind)

    colors = {
        'basic': '#098EFF',
        'special': '#30BD03',
        'rare': '#FFE500',
        'epic': '#BE52FF',
        'rarity': '#A63D42'
    }

    car_country = 'Italia'

    # изображение карточки
    if car_rarity != 'legendary':
        card_picture = Image.new('RGBA', (952, 1280), colors[car_rarity])
    else:
        card_picture = Image.open(os.path.join(f'images/design/car_cards/legendary.jpg')).convert(mode='RGBA')
    card_picture.thumbnail((1000, 1000))
    idraw = ImageDraw.Draw(card_picture)

    # изображение на карточке
    if backside:
        on_card_picture = Image.open(os.path.join(f'images/design/car_cards/backside.jpg')).convert(mode='RGBA')
    else:
        on_card_picture = Image.open(os.path.join(f'images/design/car_cards/1.jpg')).convert(mode='RGBA')

    on_card_picture = on_card_picture.resize((card_picture.width - 30, card_picture.height - 30))
    card_picture.alpha_composite(on_card_picture, (15, 15))

    if not backside:
        # серый слой
        grey_layer = Image.open(os.path.join(f'images/design/car_cards/grey_layer.png')).convert(mode='RGBA')
        grey_layer = grey_layer.resize((card_picture.width - 30, card_picture.height - 30))

        card_picture.alpha_composite(grey_layer, (15, 15))

    # изображение автомобиля
    car_picture = Image.open(os.path.join(f'images/cars/{car_brand_id}/{car_id}.png'))
    car_picture.thumbnail((600, 600))

    # изображение бренда и флага
    brand_image = Image.open(os.path.join(f'images/cars/{car_brand_id}/logo.png')).convert(mode='RGBA')
    flag_image = Image.open(os.path.join(f'images/flags/{car_country}.png')).convert(mode='RGBA')

    if len(car_brand) >= 10:
        size = 130
    else:
        size = 140
    brand_image.thumbnail((size, size))
    flag_image.thumbnail((300, 300))

    # настройки шрифта
    font_path = os.path.join('fonts/blogger_sans.ttf')

    if len(car_brand) >= 10:
        font_sizes = (70, 35)
    else:
        font_sizes = (80, 40)

    brand_font = ImageFont.truetype(font_path, size=font_sizes[0])
    model_font = ImageFont.truetype(font_path, size=font_sizes[1])
    rarity_font = ImageFont.truetype(font_path, size=45)
    characteristics_font = ImageFont.truetype(font_path, size=28)

    # добавление бренда и модели
    pos_x = (card_picture.width - (len(car_brand) * 35)) // 2 + (brand_image.width + 20) // 2
    if len(car_brand) > 12:
        for i in range(len(car_brand) - 12):
            pos_x -= 35
        pos_y_1 = 60
        pos_y_2 = 130
    else:
        pos_x = (card_picture.width - (len(car_brand) * 40)) // 2 + (brand_image.width + 20) // 2
        pos_y_1 = 60
        pos_y_2 = 135

    idraw.text((pos_x, pos_y_1), car_brand, font=brand_font, stroke_width=5, stroke_fill='black')
    idraw.text((pos_x, pos_y_2), car_model, font=model_font, stroke_width=5, stroke_fill='black')

    pos_y = 150 - brand_image.height + (25 if len(car_brand) >= 10 else 35)
    card_picture.alpha_composite(brand_image, (pos_x - brand_image.width - 20, pos_y))

    # добавление флага
    flag_image = flag_image.rotate(45, expand=True)
    card_picture.alpha_composite(flag_image, (550, -50))

    if not backside:
        # добавление редкости
        rarities = {
            'basic': ['обычная', '#098EFF'],
            'special': ['особая', '#30BD03'],
            'rare': ['редкая', '#FFE500'],
            'epic': ['эпическая', '#BE52FF'],
            'legendary': ['легендарная', os.path.join('images/design/car_cards/caption.png')],
            'rarity': ['раритет', '#A63D42']
        }

        pos_x = (card_picture.width - len(rarities[car_rarity][0]) * 21) // 2
        if car_rarity != 'legendary':
            idraw.text((pos_x, 200), rarities[car_rarity][0], font=rarity_font, fill=rarities[car_rarity][1],
                       stroke_width=4, stroke_fill='black')
        else:
            caption = Image.open(rarities[car_rarity][1])
            caption.thumbnail((280, 280))
            pos_x = (card_picture.width - caption.width) // 2
            card_picture.alpha_composite(caption, (pos_x, 220))

        # добавление автомобиля
        pos_x = (card_picture.width - car_picture.width) // 2
        pos_y = (card_picture.height - 15 - 480) + (card_picture.height - 15 - 480 - car_picture.height) // 2
        card_picture.alpha_composite(car_picture, (pos_x, pos_y))

        # добавление характеристик
        idraw.rounded_rectangle((70, 350, 340, 380), radius=10, fill='white')
        idraw.rounded_rectangle((70, 450, 340, 480), radius=10, fill='white')
        idraw.rounded_rectangle((card_picture.width - 340, 350, card_picture.width - 70, 380), radius=10, fill='white')
        idraw.rounded_rectangle((card_picture.width - 340, 450, card_picture.width - 70, 480), radius=10, fill='white')

        idraw.text((75, 315), 'Макс. скорость', font=characteristics_font, stroke_fill='black', stroke_width=3)
        idraw.text((75, 415), 'Ускорение', font=characteristics_font, stroke_fill='black', stroke_width=3)
        idraw.text((card_picture.width - 330, 315), 'Управляемость', font=characteristics_font,
                   stroke_fill='black', stroke_width=3)
        idraw.text((card_picture.width - 330, 415), 'Проходимость', font=characteristics_font,
                   stroke_fill='black', stroke_width=3)

        # установка характеристик согласно характеристикам автомобиля
        bars_length = calculate_characteristic_bar_length(car_id, 270, identified_improvements)
        idraw.rounded_rectangle((70, 350, 70 + bars_length[0], 380), radius=10, fill='#00FF25')
        idraw.rounded_rectangle((70, 450, 70 + bars_length[1], 480), radius=10, fill='#00FF25')
        idraw.rounded_rectangle((card_picture.width - 340, 350, card_picture.width - 340 + bars_length[2], 380),
                                radius=10, fill='#00FF25')
        idraw.rounded_rectangle((card_picture.width - 340, 450, card_picture.width - 340 + bars_length[3], 480),
                                radius=10, fill='#00FF25')

    # обратная сторона карточки
    if backside:
        # добавление характеристик
        characteristics_big_font = ImageFont.truetype(font_path, size=40)
        characteristics_small_font = ImageFont.truetype(font_path, size=38)

        characteristic_types = ['Мощность двигателя', 'Максимальная скорость', 'Разгон до 100 км/ч',
                                'Объем топливного бака', 'Расход топлива/100 км', 'Масса автомобиля']
        characteristics = ['963 л.с.', '350 км/ч', '3.0 с', '92 л', '330 л', '1,255 т']
        pos_y = 250
        for ch in characteristic_types:
            idraw.text((60, pos_y), f'{ch}:', font=characteristics_big_font)
            pos_y += 50

        pos_y = 250
        for ch in characteristics:
            idraw.text((530, pos_y), f'{ch}', font=characteristics_big_font, stroke_width=4, stroke_fill='black')
            pos_y += 50

        # добавление состояния автомобиля
        idraw.text((130, 820), 'Состояние', font=characteristics_small_font)
        idraw.text((130, 860), 'автомобиля:', font=characteristics_small_font)

        car_state_image = generate_car_state_picture(user_id, car_id, 220)
        card_picture.alpha_composite(car_state_image, (330, 740))

        # добавление привода
        drive_unit_type = 'rwd'

        drive_unit_image = Image.open('images/cars_parts/drive_unit/drive_unit.png').convert(mode='RGBA')
        drive_unit_image.thumbnail((200, 200))

        card_picture.alpha_composite(drive_unit_image, (500, 650))
        idraw.text((565, 850), drive_unit_type.upper(), font=characteristics_big_font)

        # установленный комлект шин
        if tires:
            tires_image = Image.open(os.path.join(f'images/cars_parts/tires/{tires[0]}.png')).convert(mode='RGBA')
            tires_image.thumbnail((150, 150))

            logo = Image.open(os.path.join(f'images/cars_parts/tires/logos/{tires[0]}.png')).convert(mode='RGBA')
            logo.thumbnail((75, 75))

            center_pos_x = 165
            center_pos_y = 675

            t_pos_x = center_pos_x - tires_image.width // 2
            t_pos_y = center_pos_y - tires_image.height // 2
            card_picture.alpha_composite(tires_image, (t_pos_x, t_pos_y))

            pos_x = t_pos_x - logo.width // 2 + 5
            pos_y = center_pos_y - logo.height // 2
            card_picture.alpha_composite(logo, (pos_x, pos_y))

            pos_x = t_pos_x + tires_image.width + 20
            pos_y = t_pos_y + 20

            caption_font = get_fonts('blogger_sans.ttf', 35)[0]

            idraw.text((pos_x, pos_y), 'Состояние:', font=caption_font, stroke_width=4, stroke_fill='black')

            default_color_value = [255, 0]
            for i in range(int(tires[1])):
                if default_color_value[1] >= 255:
                    default_color_value[0] -= 255 / 50
                else:
                    default_color_value[1] += 255 / 50

            color = (int(default_color_value[0]), int(default_color_value[1]), 0, 255)
            if tires[1] == 0:
                color = (0, 0, 0, 255)

            text = f'{tires[1]} %'
            idraw.text((pos_x + 10, pos_y + 40), text, font=caption_font, fill=color,
                       stroke_fill='black', stroke_width=4)


            # pos_x = 15 + 5
            # pos_y = card_picture.height - 15 - logo.height - 5

    if path is None:
        save_path = os.path.join(f'images/for_saves/{random.randint(100, 10000000)}.png')
    else:
        save_path = path

    card_picture.save(save_path)
    card_picture.close()

    return save_path
    # card_picture.save('main.png')
    # return card_picture

# generate_card_picture(1005532278, 4).show()


def generate_autoparts_shop(user_id: int, details_states: list, choose_detail_index=None, fast_load=False,
                            show_prices=False):
    # настройки шрифта
    font_path = os.path.join('fonts/blogger_sans.ttf')

    title_font = ImageFont.truetype(font_path, size=55)
    caption_font = ImageFont.truetype(font_path, size=30)

    if not fast_load:
        # изображение фона
        background = Image.open(os.path.join('images/design/theme_3.jpg')).convert(mode='RGBA')
        background.thumbnail((1000, 1000))

        # название раздела
        title = 'Тюнинг'

        tuning_icon = Image.open(os.path.join('images/design/icons/tuning.png')).convert(mode='RGBA')
        tuning_icon.thumbnail((80, 80))

        idraw = ImageDraw.Draw(background)
        pos_x = (background.width - len(title) * 29 + 10 + tuning_icon.width) // 2
        idraw.text((pos_x, 40), title, font=title_font)

        background.alpha_composite(tuning_icon, (pos_x - tuning_icon.width - 10, 33))

        # детали для улучшения
        detail_width = 100

        def get_detail_path(detail_name: str):
            detail_path = os.path.join(f'images/cars_parts/improvements/{detail_name}.png')
            return detail_path

        details = ['compressor', 'cylinder_block', 'camshaft', 'chip',
                   'filter', 'gearbox', 'clutch', 'differential',
                   'brakes', 'shocks', 'frame', 'weight']

        details_images = []
        detail_index = 0

        # изображения гоалочки и крестика
        on_image = Image.open(os.path.join('images/icons/checkbox.png')).convert(mode='RGBA')
        off_image = Image.open(os.path.join('images/icons/cancel.png')).convert(mode='RGBA')

        on_image.thumbnail((30, 30))
        off_image.thumbnail((30, 30))

        for detail in details:
            detail_image = Image.open(get_detail_path(detail)).convert(mode='RGBA')
            detail_height = int(detail_image.height * (detail_width / detail_image.width))
            detail_image = detail_image.resize((detail_width, detail_height))

            if details_states[detail_index] == 1:
                pos_x = detail_image.width - on_image.width
                pos_y = detail_image.height - on_image.height
                detail_image.alpha_composite(on_image, (pos_x, pos_y))
            if details_states[detail_index] == 2:
                pos_x = detail_image.width - off_image.width
                pos_y = detail_image.height - off_image.height
                detail_image.alpha_composite(off_image, (pos_x, pos_y))

            detail_index += 1

            details_images.append(detail_image)

        details_names = ['Компрессор', 'Блок цилиндров', 'Распредвал', 'Чип-тюнинг',
                         'Фильтр', 'Коробка передач', 'Сцепление', 'Дифференциал',
                         'Тормоза', 'Амортизаторы', 'Каркас', 'Снижение массы']

        pos_x = 150
        pos_y = 235

        for detail_index in range(len(details_names)):
            detail = details_names[detail_index]
            detail_price = 1_000_000
            detail_price_str = f'345 500$'

            if show_prices:
                caption = detail_price_str
            else:
                caption = detail

            detail_image = details_images[detail_index]
            detail_pos_x = pos_x - detail_image.width // 2
            detail_pos_y = pos_y - detail_image.height

            background.alpha_composite(detail_image, (detail_pos_x, detail_pos_y))

            caption_pos_x = pos_x - (len(caption) * (15 if show_prices else 16) // 2)
            caption_pos_y = detail_pos_y + detail_image.height + 15

            idraw.text((caption_pos_x, caption_pos_y), caption, font=caption_font)

            if detail_index in [3, 7, 11]:
                pos_x = 150
                pos_y += 170
            else:
                pos_x += 230

        save_path = os.path.join(f'images/for_saves/{user_id}/02.png')
        background.save(save_path)

    else:
        file_name = '02.png'

        background = Image.open(os.path.join(f'images/for_saves/{user_id}/{file_name}')).convert(mode='RGBA')
        background.thumbnail((1000, 1000))

        idraw = ImageDraw.Draw(background)

    positions = [(60, 125, 240, 290), (258, 125, 502, 290), (520, 125, 700, 290), (750, 125, 930, 290),
                 (92, 295, 215, 460), (250, 295, 500, 460), (528, 295, 692, 460), (734, 295, 961, 460),
                 (84, 465, 216, 630), (274, 465, 486, 630), (552, 465, 668, 630), (718, 465, 962, 630)]

    positions_for_prices = [(80, 125, 220, 290), (310, 125, 450, 290), (540, 125, 680, 290), (770, 125, 910, 290),
                            (80, 295, 220, 460), (310, 295, 450, 460), (540, 295, 680, 460), (770, 295, 910, 460),
                            (80, 465, 220, 630), (310, 465, 450, 630), (540, 465, 680, 630), (770, 465, 910, 630)]

    if not show_prices:
        idraw.rounded_rectangle(positions[choose_detail_index], radius=10, fill=None, width=3)
    else:
        idraw.rounded_rectangle(positions_for_prices[choose_detail_index], radius=10, fill=None, width=3)

    save_path = os.path.join(f'images/for_saves/{user_id}/{random.randint(100, 100000000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_car_part_image(user_id, car_part_index, car_id, car_part_status=0):
    car_part = car_parts_list[car_part_index]

    brand_id = cursor.execute("SELECT car_brand FROM cars WHERE id = ?", (car_id,)).fetchone()[0]
    user_car_parts_amount = \
        cursor.execute(f"SELECT {car_part} FROM user_car_parts_amount WHERE user_id = ?",
                       (user_id,)).fetchone()[0]

    car_part_title = car_parts_short[car_part]
    car_part_title_2 = car_parts[car_part]
    car_part_amount = car_parts_prices_and_amounts[car_part][1]
    car_part_price = car_parts_prices_and_amounts[car_part][0]

    identified_improvements = []
    improvements = list(cursor.execute("SELECT * FROM users_cars WHERE car_id = ?", (car_id,)).fetchone())[2:-1]
    for index in range(len(improvements)):
        if improvements[index] == 1 and index != car_part_index:
            identified_improvements.append(index)

    # настройки шрифта
    font_path = os.path.join('fonts/blogger_sans.ttf')

    title_font = ImageFont.truetype(font_path, size=60)
    sticker_font = ImageFont.truetype(font_path, size=50)
    caption_font = ImageFont.truetype(font_path, size=40)
    characteristics_font = ImageFont.truetype(font_path, size=25)

    # фон
    background = Image.open(os.path.join('images/design/theme_3.jpg')).convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    album = Image.open(os.path.join('images/design/other_pictures/album.jpg')).convert(mode='RGBA')

    idraw = ImageDraw.Draw(background)
    idraw_album = ImageDraw.Draw(album)

    # название детали
    title_width = idraw.textsize(car_part_title_2, font=title_font)[0]
    pos_x = (background.width - title_width) // 2
    idraw.text((pos_x, 40), car_part_title_2, font=title_font, stroke_fill='black', stroke_width=6)

    # альбом
    detail_image = Image.open(os.path.join(f'images/cars_parts/improvements/{car_part}.png')).convert(mode='RGBA')
    detail_image.thumbnail((700, 700))
    # detail_image = detail_image.rotate(-5, expand=True)

    center_x = album.width // 2
    center_y = album.height // 2 - int(album.height * 0.05)

    pos_x = center_x - detail_image.width // 2
    pos_y = center_y - detail_image.height // 2

    album.alpha_composite(detail_image, (pos_x, pos_y))

    for font_size in range(180, 10, -1):
        font = get_fonts('blogger_sans.ttf', font_size)[0]
        text_width, text_height = idraw_album.textsize(car_part_title, font=font)
        if text_width + int(album.width * 0.15) <= album.width:
            pos_x = (album.width - text_width) // 2
            pos_y = int(album.height * 0.8 + (album.height * 0.2 - text_height) // 2)
            idraw_album.text((pos_x, pos_y), car_part_title, font=font, fill='black')
            break

    album = album.rotate(-2, expand=True)
    album.thumbnail((370, 370))

    # стикер
    sticker = Image.open(os.path.join(f'images/design/other_pictures/sticker.png'))
    sticker.thumbnail((150, 150))

    idraw_sticker = ImageDraw.Draw(sticker)
    idraw_sticker.text((50, 23), f'x{car_part_amount}', font=sticker_font, fill='black')
    sticker = sticker.rotate(45, expand=True)

    # накладывание альбома и стикера на фон
    pos_x = 90
    pos_y = 140
    background.alpha_composite(album, (pos_x, pos_y))
    background.alpha_composite(sticker, (pos_x - 30, pos_y - 35))

    # наличие и статус детали
    idraw.text((100, 590), f'Наличие: x{user_car_parts_amount}', font=caption_font, stroke_fill='black', stroke_width=4)
    pos_x = 100
    if car_part_status == 1:
        checkbox_icon = Image.open(os.path.join(f'images/icons/checkbox.png'))
        checkbox_icon.thumbnail((40, 40))

        caption = 'Установлено'

        background.alpha_composite(checkbox_icon, (340, 537))
    elif car_part_status == 2:
        checkbox_icon = Image.open(os.path.join(f'images/icons/cancel.png'))
        checkbox_icon.thumbnail((40, 40))

        caption = 'Снято'

        background.alpha_composite(checkbox_icon, (215, 537))
    else:
        caption = '$'
        bit_counter = 0
        for str_index in range(len(str(car_part_price)) - 1, -1, -1):
            if bit_counter % 3 == 0 and bit_counter != 0:
                caption = ' ' + caption
            caption = str(car_part_price)[str_index] + caption
            bit_counter += 1

        caption = f'Цена: {caption}'

    idraw.text((pos_x, 540), caption, font=caption_font, stroke_fill='black', stroke_width=4)

    # # добавление характеристик
    pos_x = background.width // 2
    pos_y = 290
    characteristics = ['Ускорение:', 'Проходимость:', 'Макс. скорость:', 'Управляемость:']
    indexes = [1, 3, 0, 2]
    for el in range(4):
        if el == 2:
            pos_y -= 80
            pos_x = background.width // 2

        rect_width_1 = calculate_characteristic_bar_length(car_id, 190, identified_improvements)[indexes[el]]
        rect_width_2 = \
            calculate_characteristic_bar_length(car_id, 190, identified_improvements + [car_part_index])[indexes[el]]

        idraw.rounded_rectangle((pos_x, pos_y, pos_x + 190, pos_y + 30), radius=15, fill='white')
        if car_part_status == 1:
            color = 'red'
        else:
            color = '#00FF25'

        idraw.rounded_rectangle((pos_x, pos_y, pos_x + rect_width_2, pos_y + 30), radius=15, fill=color)
        idraw.rounded_rectangle((pos_x, pos_y, pos_x + rect_width_1, pos_y + 30), radius=15, fill='#098EFF')
        idraw.text((pos_x + 5, pos_y - 30), characteristics[el], font=characteristics_font, stroke_width=3,
                   stroke_fill='black')
        pos_x += 220

    # изображение автомобиля
    car_image = Image.open(os.path.join(f'images/cars/{brand_id}/{car_id}.png'))
    car_image.thumbnail((400, 400))

    pos_x = background.width // 2 + ((220 + 190 - car_image.width) // 2)
    pos_y = 290 + (background.height - (290 + 30) - car_image.height) // 2 + 30

    background.alpha_composite(car_image, (pos_x, pos_y))

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 10000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_car_collection_menu_image(car_brands: list, choose_brand_index: int):
    # фон
    background = Image.open(os.path.join('images/design/theme.jpg')).convert(mode='RGBA')
    background.thumbnail((1000, 1000))
    background = background.resize((1000, int(background.height * 1.1)))

    idraw = ImageDraw.Draw(background)

    # настройки шрифта
    title_font, brand_font = get_fonts('blogger_sans.ttf', 60, 35)

    # название раздела
    title = 'Коллекция автомобилей'

    pos_x = (background.width - len(title) * 30) // 2
    idraw.text((pos_x, 50), title, font=title_font)

    # добавление брендов
    pos_x = 200
    pos_y = 250
    # for brand_id in list(car_brands.keys()):
    brand_rows = [[]]
    for brand_id in car_brands:
        brand_logo = Image.open(os.path.join(f'images/cars/{brand_id}/logo.png')).convert(mode='RGBA')
        brand_logo.thumbnail((150, 150))
        if len(brand_rows[-1]) < 3:
            brand_rows[-1].append([brand_id, brand_logo])
        else:
            brand_rows.append([[brand_id, brand_logo]])

    brand_index = 0
    for brand_row in brand_rows:
        max_brand_logo_height = max(brand_row[0][1].height, brand_row[1][1].height, brand_row[2][1].height)
        caption_pos_y = pos_y + max_brand_logo_height // 2 + 20
        for brand_id, brand_logo in brand_row:
            brand = cars_brands[brand_id]
            background.alpha_composite(brand_logo, (pos_x - brand_logo.width // 2, pos_y - brand_logo.height // 2))

            brand_len = 0
            for letter in brand:
                if letter != letter.lower():
                    brand_len += 26
                else:
                    brand_len += 14

            caption_pos_x = pos_x - brand_len // 2

            idraw.text((caption_pos_x, caption_pos_y), brand, font=brand_font)

            if brand_index == choose_brand_index:
                x_1 = min(caption_pos_x, pos_x - brand_logo.width // 2) - 15
                y_1 = pos_y - max_brand_logo_height // 2 - 15
                x_2 = x_1 + (pos_x - x_1) * 2
                y_2 = caption_pos_y + 40

                idraw.rounded_rectangle((x_1, y_1, x_2, y_2), radius=10, fill=None, width=3)

            brand_index += 1

            pos_x += 300
        pos_x = 200
        pos_y += 270

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 10000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_brand_image(brand_id: int):
    text = 'Ferrari — итальянская компания, выпускающая\n' \
           'спортивные и гоночные автомобили, базирующаяся\n' \
           'в Маранелло. Основанная в 1947 году Энцо Феррари,\n' \
           'она спонсировала гонщиков и производила гоночные\n' \
           'автомобили до 1947 года. С 1947 года начала\n' \
           'выпуск спортивных автомобилей, разрешённых к\n' \
           'использованию на дорогах общего пользования, под\n' \
           'маркой «Ferrari S.p.A.».'

    # фон
    background = Image.open(os.path.join('images/design/theme.jpg')).convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(background)

    # настройка шрифтов
    title_font, text_font, progress_font = get_fonts('blogger_sans.ttf', 60, 26, 30)

    # заголовок
    title = cars_brands[brand_id]
    pos_x = (background.width - len(title) * 28) // 2
    idraw.text((pos_x, 40), title, font=title_font)

    # лого бренда
    brand_logo = Image.open(os.path.join(f'images/cars/{brand_id}/logo.png')).convert(mode='RGBA')
    brand_logo.thumbnail((250, 250))

    pos_y = 250
    background.alpha_composite(brand_logo, (70, pos_y - brand_logo.height // 2))

    # информация о бренде
    text = text.split('\n')
    pos_y = 130
    for row in text:
        idraw.text((70 + brand_logo.width + 40, pos_y), row, font=text_font)
        pos_y += 30

    # два автомобиля
    brand_cars_ids = [i[0] for i in cursor.execute("SELECT id FROM cars WHERE car_brand = ?",
                                                   (brand_id,)).fetchall()]

    car_1 = random.choice(brand_cars_ids)
    brand_cars_ids.remove(car_1)
    car_2 = random.choice(brand_cars_ids)

    car_1_image = Image.open(os.path.join(f'images/cars/{brand_id}/{car_1}.png')).convert(mode='RGBA')
    car_2_image = Image.open(os.path.join(f'images/cars/{brand_id}/{car_2}.png')).convert(mode='RGBA')

    car_1_image.thumbnail((280, 280))
    car_2_image.thumbnail((280, 280))

    car_2_image = car_2_image.transpose(Image.FLIP_LEFT_RIGHT)

    pos_x = 450
    pos_y = 560
    background.alpha_composite(car_1_image, (pos_x, pos_y - car_1_image.height))
    background.alpha_composite(car_2_image, (pos_x + 200, pos_y - car_2_image.height + 50))

    # шкала прогресса
    progress_str = '24/49'

    idraw.rounded_rectangle((70, 520, 370, 540), radius=10, fill='white', width=3, outline='white')
    pos_x = 370
    idraw.text(((300 - len(progress_str) * 16) // 2 + 70, 480), progress_str, font=progress_font)

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 10000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_tires_card_image(tires: str, wear: int):
    # изображение карточки
    card_image = Image.open(os.path.join(f'images/cars_parts/tires/{tires}.jpg')).convert(mode='RGBA')
    card_image.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(card_image)

    # настройка шрифта
    caption_font = get_fonts('blogger_sans.ttf', 45)[0]

    # значок автомобиля
    car_icon = Image.open(os.path.join('images/car_states/tires/body.png')).convert(mode='RGBA')
    car_icon.thumbnail((150, 150))

    wheels_icon = Image.open(os.path.join('images/car_states/tires/tires.png')).convert(mode='RGBA')
    wheels_icon.thumbnail((150, 150))

    # покраска колес
    default_color_value = [255, 0]
    for i in range(wear):
        if default_color_value[1] >= 255:
            default_color_value[0] -= 255 / 50
        else:
            default_color_value[1] += 255 / 50

    color = (int(default_color_value[0]), int(default_color_value[1]), 0, 255)
    if wear == 0:
        color = (0, 0, 0, 255)

    new_image = []
    for pixel in wheels_icon.getdata():
        if pixel[-1] != 0:
            new_image.append(color)
        else:
            new_image.append(pixel)

    wheels_icon = Image.new(wheels_icon.mode, wheels_icon.size)
    wheels_icon.putdata(new_image)

    # наложение колес на значок автомобиля
    car_icon.alpha_composite(wheels_icon)

    # наложение значка автомобиля на карточку
    caption = 'Износ:'
    idraw.text((225, 515), caption, font=caption_font)

    card_image.alpha_composite(car_icon, (375, 460))

    # характеристики шин
    def get_bar_length(percentages: int):
        full_length = 284
        bar_length = int(full_length * (percentages / 100))

        return bar_length

    idraw.rounded_rectangle((66, 299, 66 + get_bar_length(tires_characteristics[tires][0]), 333),
                            radius=20, fill='#0AF104')
    idraw.rounded_rectangle((66, 427, 66 + get_bar_length(tires_characteristics[tires][2]), 461),
                            radius=20, fill='#0AF104')
    idraw.rounded_rectangle((400, 299, 400 + get_bar_length(tires_characteristics[tires][1]), 333),
                            radius=20, fill='#0AF104')
    idraw.rounded_rectangle((400, 427, 400 + get_bar_length(tires_characteristics[tires][3]), 461),
                            radius=20, fill='#0AF104')

    return card_image


def generate_garage_picture(user_id, car_id, show_menu=False, menu_index=0):
    size = 600
    bottom_margin = 40

    if show_menu:
        background = Image.open(os.path.join(f'images/for_saves/{user_id}/03.png')).convert(mode='RGBA')
        menu_image = Image.open(os.path.join(f'images/design/garage_menu/{menu_index}.png'))
        menu_image.thumbnail((1000, 1000))

        background.alpha_composite(menu_image, (0, 0))

        save_path = os.path.join(f'images/for_saves/{random.randint(100, 1000000000)}.png')
        background.save(save_path)
        background.close()

        return save_path

    # фон
    background = Image.open(os.path.join('images/design/theme_2.jpg')).convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(background)

    # шрифт
    brand_font, model_font = get_fonts('blogger_sans.ttf', 70, 30)

    # автомобиль
    brand_id = cursor.execute("SELECT car_brand FROM cars WHERE id = ?", (car_id,)).fetchone()[0]

    car_image = Image.open(os.path.join(f'images/cars/{brand_id}/{car_id}.png'))
    car_image.thumbnail((size, size))

    pos_x = (background.width - car_image.width) // 2
    pos_y = background.height - car_image.height - bottom_margin
    background.alpha_composite(car_image, (pos_x, pos_y))

    # бренд и модель автомобиля
    car_brand = cars_brands[brand_id]
    car_model = cursor.execute("SELECT car_model FROM cars WHERE id = ?", (car_id,)).fetchone()[0]

    brand_logo = Image.open(os.path.join(f'images/cars/{brand_id}/logo.png'))
    brand_logo.thumbnail((100, 100))

    text_brand_width = idraw.textsize(car_brand, font=brand_font)[0]
    text_model_width = idraw.textsize(car_model, font=model_font)[0]

    x_1 = background.width // 2 - (text_brand_width + brand_logo.width) // 2 - 50
    x_2 = background.width - x_1

    text_pos_x = x_1 + brand_logo.width + 50

    idraw.rounded_rectangle((x_1, 50, x_2, 190), radius=10, fill=(255, 255, 255, 220), outline='black', width=1)

    idraw.text((text_pos_x, 75), car_brand, font=brand_font, stroke_width=5, stroke_fill='black')
    idraw.text((text_pos_x + text_brand_width - text_model_width, 140), car_model, font=model_font,
               stroke_width=4, stroke_fill='black')

    background.alpha_composite(brand_logo, (x_1 + ((text_pos_x - x_1) - brand_logo.width) // 2,
                                            50 + (140 - brand_logo.height) // 2))

    save_path = os.path.join(f'images/for_saves/{user_id}/03.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_tires_menu_picture(user_id, car_id, choose_tires_index):
    tires_amount = cursor.execute("SELECT * FROM user_tires_amount WHERE (user_id, car_id) = (?, ?)",
                                  (user_id, car_id)).fetchone()[2:]
    # шрифты
    caption_font = get_fonts('blogger_sans.ttf', 35)[0]

    # фон
    background = Image.open(os.path.join('images/design/tires_menu.jpg')).convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(background)

    rect_positions = [(50, 140, 250, 370), (280, 140, 490, 370), (520, 140, 740, 370), (760, 140, 980, 370),
                      (140, 390, 350, 630), (380, 390, 610, 630), (650, 390, 850, 630)]
    centers = [150, 390, 630, 870, 250, 500, 750]

    pos_y = 330
    for ind in range(7):
        text_width = idraw.textsize(f'x{tires_amount[ind]}', font=caption_font)[0]

        pos_x = centers[ind] - text_width // 2

        idraw.text((pos_x, pos_y), f'x{tires_amount[ind]}', font=caption_font, fill='white', stroke_width=4,
                   stroke_fill='black')

        if ind == 3:
            pos_y += 260

        if ind == choose_tires_index:
            idraw.rounded_rectangle(rect_positions[ind], radius=10, fill=None, outline='white', width=5)

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 10000000000)}.png')
    background.save(save_path)
    background.close()

    return save_path


def generate_tires_management_menu_picture(user_id, car_id, choose_tires_index):
    tires_amount = cursor.execute("SELECT * FROM user_tires_amount WHERE (user_id, car_id) = (?, ?)",
                                  (user_id, car_id)).fetchone()[2:]
    # шрифты
    title_font, caption_font, info_font = get_fonts('blogger_sans.ttf', 60, 30, 40)

    # фон
    background = Image.open(os.path.join('images/design/theme_3.jpg')).convert(mode='RGBA')
    background.thumbnail((1000, 1000))

    idraw = ImageDraw.Draw(background)

    tires_types = ['Мягкие', 'Средние', 'Жёсткие', 'Дождевые', 'Раллийные', 'Для бездорожья', 'Драговые']
    tires_names = {
        'Мягкие': 'soft',
        'Средние': 'medium',
        'Жёсткие': 'hard',
        'Дождевые': 'rain',
        'Раллийные': 'rally',
        'Для бездорожья': 'off_road',
        'Драговые': 'drag'
    }

    # название шин
    title = tires_types[choose_tires_index]

    tires_logo = Image.open(os.path.join(f'images/cars_parts/tires/logos/{tires_names[title]}.png'))
    tires_logo.thumbnail((90, 90))

    title_width = idraw.textsize(title, font=title_font)[0] + tires_logo.width + 15
    pos_x = (background.width - title_width) // 2

    background.alpha_composite(tires_logo, (pos_x, 25))
    idraw.text((pos_x + tires_logo.width + 15, 45), title, font=title_font, stroke_fill='black', stroke_width=6)

    # изображение шин
    tires_image = Image.open(os.path.join(f'images/cars_parts/tires/{tires_names[title]}.png'))
    tires_image.thumbnail((250, 250))

    rotated_tires_image = tires_image.rotate(90, expand=True)

    pos_y = 420
    pos_x = [60, 75, 65]

    cf = 1.8
    if choose_tires_index == 4 or choose_tires_index == 5:
        cf = 2

    for i in range(3):
        background.alpha_composite(rotated_tires_image, (pos_x[i], pos_y))
        pos_y -= int(tires_image.width / cf)

    background.alpha_composite(tires_image, (int(tires_image.height * 1.1),
                                             background.height - int(tires_image.height * 1.25)))

    # характеристики шин
    def get_bar_length(percentages: int):
        full_length = 230
        bar_length = int(full_length * (percentages / 100))

        return bar_length

    dict_key = tires_names[title]

    pos_x = 450
    pos_y = 200

    captions = ['Сцепление с|трассой (сухо):', 'Сцепление с|трассой (дождь):', 'Износостойкость:', 'Проходимость:']
    for i in range(4):
        idraw.rounded_rectangle((pos_x, pos_y, pos_x + 230, pos_y + 35), radius=20, fill='white')
        idraw.rounded_rectangle((pos_x, pos_y, pos_x + get_bar_length(tires_characteristics[dict_key][i]), pos_y + 35),
                                radius=20, fill='#098EFF')
        caption = captions[i].split('|')
        if len(caption) > 1:
            idraw.text((pos_x + 25, pos_y - 65), caption[0], font=caption_font, stroke_fill='black', stroke_width=3)
            if i == 0:
                idraw.text((pos_x + 17, pos_y - 35), caption[1], font=caption_font, stroke_fill='black', stroke_width=3)
            else:
                idraw.text((pos_x + 5, pos_y - 35), caption[1], font=caption_font, stroke_fill='black', stroke_width=3)
        else:
            text_width = idraw.textsize(caption[0], font=caption_font)[0]
            idraw.text((pos_x + (230 - text_width) // 2, pos_y - 35), caption[0], font=caption_font,
                       stroke_fill='black', stroke_width=3)

        pos_x += 260
        if i == 1:
            pos_y += 100
            pos_x = 450

    # прочая информация
    tires_amount = tires_amount[choose_tires_index]
    info = ['Наличие', 'Вместимость', 'Стоимость']
    pos_x = int(tires_image.height * 1.1) + tires_image.width + 50
    pos_y = 400
    for cap in info:
        text_width = idraw.textsize(cap, font=info_font)[0]
        idraw.text((pos_x, pos_y), f'{cap}:', font=info_font, stroke_fill='black', stroke_width=3)
        if cap == 'Наличие':
            if tires_amount == 0:
                color = 'white'
            else:
                color = '#0AF104'
            value = f'x{tires_amount}'
        if cap == 'Вместимость':
            value = 'x5'
            color = 'white'
        if cap == 'Стоимость':
            tires_price = tires_prices[dict_key]
            value = get_displayed_price(tires_price)
            color = 'white'

        idraw.text((pos_x + text_width + 30, pos_y), value, font=info_font, fill=color,
                   stroke_fill='black', stroke_width=3)

        pos_y += 60

    save_path = os.path.join(f'images/for_saves/{random.randint(100, 10000000000)}.png')
    background.save(save_path)
    background.close()

    return save_path

# generate_tires_management_menu_picture(1005532278, 4, 6).show()
