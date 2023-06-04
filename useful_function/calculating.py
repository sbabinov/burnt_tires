import random

from objects_data import *
from loader import cursor


def calculate_characteristic_bar_length(car_id, full_bar_length, identified_improvements: list = None, user_id=None):
    max_speed = int(cursor.execute("SELECT max_speed FROM cars WHERE id = ?", (car_id,)).fetchone()[0])
    acceleration_time = float(cursor.execute("SELECT acceleration_time FROM cars WHERE id = ?",
                                             (car_id,)).fetchone()[0])
    handling = int(cursor.execute("SELECT handling FROM cars WHERE id = ?", (car_id,)).fetchone()[0])
    passability = int(cursor.execute("SELECT passability FROM cars WHERE id = ?", (car_id,)).fetchone()[0])

    if identified_improvements is None:
        identified_improvements = cursor.execute("SELECT * FROM users_cars WHERE (user_id, car_id) = (?, ?)",
                                                 (user_id, car_id)).fetchone()[2: -2]

    characteristics = {
        'max_speed': max_speed,
        'acceleration_time': acceleration_time,
        'handling': handling,
        'passability': passability
    }

    new_characteristics = characteristics.copy()

    for car_part_index in identified_improvements:
        car_part = car_parts_list[car_part_index]
        for improvement in list(car_parts_coefficient[car_part].keys()):
            new_characteristics[improvement] += \
                characteristics[improvement] * car_parts_coefficient[car_part][improvement] - \
                characteristics[improvement]

    max_speed = new_characteristics['max_speed']
    acceleration_time = new_characteristics['acceleration_time']
    handling = new_characteristics['handling']
    passability = new_characteristics['passability']

    speed_percentages = (max_speed - 100) * 100 / 300
    speed_bar_length = full_bar_length * speed_percentages // 100

    if acceleration_time >= 9:
        acceleration_percentages = 10
    else:
        acceleration_percentages = abs(acceleration_time - 10) * 100 / 10
    acceleration_bar_length = full_bar_length * acceleration_percentages // 100

    handling_bar_length = full_bar_length * handling // 100
    passability_bar_length = full_bar_length * passability // 100

    return [speed_bar_length, acceleration_bar_length, handling_bar_length, passability_bar_length]


def calculate_score(race_id, user_id, element_id, car_id, tires):
    weather = cursor.execute("SELECT weather FROM races WHERE id = ?", (race_id,)).fetchone()[0]
    # tires = ['soft', 100]

    improvements = cursor.execute("SELECT * FROM users_cars WHERE (user_id, car_id) = (?, ?)",
                                  (user_id, car_id)).fetchone()[2:-2]
    driving_exp = cursor.execute("SELECT driving_exp FROM users_cars WHERE (user_id, car_id) = (?, ?)",
                                 (user_id, car_id)).fetchone()[0] / 10
    identified_improvements = []
    for ind in range(len(improvements)):
        if improvements[ind] == 1:
            identified_improvements.append(ind)

    speed, acceleration, handling, passability = \
        calculate_characteristic_bar_length(car_id, 100, identified_improvements)

    characteristics = {
        'speed': speed,
        'acceleration': acceleration,
        'handling': handling,
        'passability': passability + driving_exp
    }

    score = 0
    priority_characteristics = []
    if element_id == 0:
        priority_characteristics = [['acceleration', 1]]
    elif element_id == 1:
        priority_characteristics = [['acceleration', 0.5], ['speed', 0.5]]
    elif element_id == 2:
        priority_characteristics = [['speed', 0.3], ['acceleration', 0.7]]
    elif element_id == 3:
        priority_characteristics = [['handling', 0.5], ['acceleration', 0.5]]
    elif element_id == 4:
        priority_characteristics = [['handling', 0.6], ['acceleration', 0.4]]
    elif element_id == 5:
        priority_characteristics = [['handling', 0.3], ['speed', 0.7]]
    elif element_id == 6:
        priority_characteristics = [['handling', 0.7], ['acceleration', 0.3]]

    for c in priority_characteristics:
        score += characteristics[c[0]] * c[1]

    if weather == 'rain' or weather == 'shower':
        if tires[0] == 'rain':
            tires_score = tires_characteristics[tires[0]][1] * tires[1] // 400
        else:
            tires_score = tires_characteristics[tires[0]][1] * 1.5 * tires[1] // 400
    else:
        tires_score = tires_characteristics[tires[0]][0] * tires[1] // 400

    score += tires_score

    return int(score)


def change_tires_wear(tires, race_id, element_id):
    weather = cursor.execute("SELECT weather FROM races WHERE id = ?", (race_id,)).fetchone()[0]
    if element_id in [0, 1, 2, 5]:
        ind1 = 0
        ind2 = 1
    else:
        ind1 = 1
        ind2 = 2

    if weather == 'rain' or weather == 'shower':
        wear_borders = tires_wear['rain']
        wear = random.randint(wear_borders[ind1], wear_borders[ind2]) / 10
    else:
        wear_borders = tires_wear[tires[0]]
        wear = random.randint(wear_borders[ind1], wear_borders[ind2]) / 10

    new_wear = tires[1] - wear
    return new_wear

# print(calculate_score(6, 1005532278, 0, 4, ['medium', 0]))
