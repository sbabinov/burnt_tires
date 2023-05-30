import random

from objects_data import *
from loader import cursor, connection


def update_driving_experience(user_id, car_id):
    current_exp = cursor.execute("SELECT driving_exp FROM users_cars WHERE (user_id, car_id) = (?, ?)",
                                 (user_id, car_id)).fetchone()[0]
    car_passability = cursor.execute("SELECT passability FROM cars WHERE id = ?", (car_id,)).fetchone()[0]
    max_exp = 1000 - car_passability * 10

    new_exp = current_exp + 5
    if new_exp > max_exp:
        new_exp = max_exp

    cursor.execute("UPDATE users_cars SET driving_exp = ? WHERE (user_id, car_id) = (?, ?)",
                   (new_exp, user_id, car_id))
    connection.commit()
