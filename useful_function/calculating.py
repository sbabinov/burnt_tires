from objects_data import *
from loader import cursor


def calculate_characteristic_bar_length(car_id, full_bar_length, identified_improvements: list):
    max_speed = int(cursor.execute("SELECT max_speed FROM cars WHERE id = ?", (car_id,)).fetchone()[0])
    acceleration_time = float(cursor.execute("SELECT acceleration_time FROM cars WHERE id = ?",
                                             (car_id,)).fetchone()[0])
    handling = int(cursor.execute("SELECT handling FROM cars WHERE id = ?", (car_id,)).fetchone()[0])
    passability = int(cursor.execute("SELECT passability FROM cars WHERE id = ?", (car_id,)).fetchone()[0])

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

# print(calculate_characteristic_bar_length(4, 1000, [0, 1, 2]))