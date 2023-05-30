tires_characteristics = {
        'soft': [80, 20, 30, 15],
        'medium': [65, 26, 50, 20],
        'hard': [50, 32, 70, 25],
        'rain': [35, 80, 70, 20],
        'rally': [35, 25, 80, 70],
        'off_road': [35, 25, 90, 90],
        'drag': [90, 10, 20, 10]
}

tires_prices = {
        'soft': 10000,
        'medium': 10000,
        'hard': 10000,
        'rain': 10000,
        'rally': 10000,
        'off_road': 10000,
        'drag': 10000
}

# прямая, затяжной поворот | повороты
tires_wear = {
        'soft': [25, 30, 35],
        'medium': [18, 21, 25],
        'hard': [10, 12, 15],
        'rain': [15, 17, 20],
        'rally': [10, 15, 20],
        'off_road': [10, 15, 20],
        'drag': [35, 40, 45]
}

car_parts = {
        'compressor': 'Турбокомпрессор',
        'cylinder_block': 'Блок цилиндров',
        'camshaft': 'Распределительный вал',
        'chip': 'Чип-тюнинг',
        'filter': 'Воздушный фильтр',
        'gearbox': 'Коробка переключения передач',
        'clutch': 'Сцепление',
        'differential': 'Дифференциал',
        'brakes': 'Тормозная система',
        'shocks': 'Амортизаторы',
        'frame': 'Защитный каркас',
        'weight': 'Снижение массы автомобиля',
    }

car_parts_short = {
        'compressor': 'Турбокомпрессор',
        'cylinder_block': 'Блок цилиндров',
        'camshaft': 'Распредвал',
        'chip': 'Чип-тюнинг',
        'filter': 'Фильтр',
        'gearbox': 'КПП',
        'clutch': 'Сцепление',
        'differential': 'Дифференциал',
        'brakes': 'Тормоза',
        'shocks': 'Амортизаторы',
        'frame': 'Каркас',
        'weight': 'Снижение массы',
}

car_parts_prices_and_amounts = {
        'compressor': [100000, 5],
        'cylinder_block': [100000, 5],
        'camshaft': [100000, 5],
        'chip': [100000, 5],
        'filter': [100000, 5],
        'gearbox': [100000, 5],
        'clutch': [100000, 5],
        'differential': [100000, 5],
        'brakes': [100000, 5],
        'shocks': [100000, 5],
        'frame': [100000, 5],
        'weight': [100000, 5],
}

car_parts_coefficient = {
        'compressor': {'acceleration_time': 0.95},
        'cylinder_block': {'max_speed': 1.07, 'acceleration_time': 0.95},
        'camshaft': {'max_speed': 1.07, 'acceleration_time': 0.97},
        'chip': {'max_speed': 1.2, 'acceleration_time': 0.8},
        'filter': {'max_speed': 1.03},
        'gearbox': {'acceleration_time': 0.8, 'handling': 1.1},
        'clutch': {'acceleration_time': 0.9, 'handling': 1.1},
        'differential': {'handling': 1.1},
        'brakes':  {'handling': 1.1},
        'shocks':  {'handling': 1.1},
        'frame':  {},
        'weight':  {'handling': 1.05},
}


car_parts_list = list(car_parts.keys())
