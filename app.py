from loader import connection, cursor


async def on_startup(dp):
    from utils.notify_admins import on_startup_notify

    await on_startup_notify(dp)
    print("Бот запущен")

    from utils.set_bot_commands import set_default_commands

    await set_default_commands(dp)

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INT,
                    username TEXT,
                    balance BIGINT,
                    cars TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS cars (
                    id INT,
                    car_brand INT,
                    car_model TEXT,
                    power INT,
                    max_speed INT,
                    acceleration_time TEXT,
                    fuel_volume INT,
                    fuel_consumption TEXT,
                    weight TEXT,
                    drive_unit_type TEXT,
                    handling INT,
                    passability INT,
                    rarity TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS races (
                    id INT,
                    type INT,
                    members TEXT,
                    race_circuit INT,
                    voted_users TEXT,
                    laps INT,
                    weather TEXT,
                    current_element_index INT,
                    pitstops INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS race_circuits (
                    id INT,
                    name TEXT,
                    elements TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS race_search (
                    user_id INT,
                    race_type INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS race_confirmations (
                      id INT,
                      confirmations TEXT,
                      race_id INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS track_elements (
                    id INT,
                    type TEXT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS users_cars (
                    user_id INT,
                    car_id INT,
                    compressor INT,
                    cylinder_block INT,
                    shaft INT,
                    chip INT,
                    filter INT,
                    gearbox INT,
                    clutch INT,
                    differential INT,
                    brakes INT,
                    shocks INT,
                    frame INT,
                    weight INT,
                    tires TEXT,
                    driving_exp INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS cars_body_state (
                    user_id INT,
                    car_id INT,
                    front INT,
                    rear INT,
                    roof INT,
                    right_side INT,
                    left_side INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS current_user_message (
                    user_id INT,
                    message_id INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS user_car_parts_amount (
                    user_id INT,
                    compressor INT,
                    cylinder_block INT,
                    shaft INT,
                    chip INT,
                    filter INT,
                    gearbox INT,
                    clutch INT,
                    differential INT,
                    brakes INT,
                    shocks INT,
                    frame INT,
                    weight INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS user_tires_amount (
                    user_id INT,
                    car_id INT,
                    soft INT,
                    medium INT,
                    hard INT,
                    rain INT,
                    rally INT,
                    off_road INT,
                    drag INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS service_data (
                    user_id INT,
                    brand_page_index INT,
                    choose_brand_index INT,
                    choose_brand_id INT,
                    car_page_index INT,
                    choose_car_index INT,
                    brand_id INT,
                    choose_detail_index INT,
                    car_id INT,
                    show_prices INT,
                    garage_menu_index INT,
                    car_part_index INT,
                    choose_tires_index INT,
                    race_confirmation_id INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS user_car_deck (
                    user_id INT,
                    preview_car INT,
                    car_1 INT,
                    car_2 INT,
                    car_3 INT,
                    car_4 INT)""")

    connection.commit()


# запуск бота
if __name__ == "__main__":
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
