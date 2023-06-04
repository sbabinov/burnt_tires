import random


def get_result_by_chance(chance: int):
    numbers = list(range(100))
    appropriate_numbers = list(range(chance))
    number = random.choice(numbers)
    if number in appropriate_numbers:
        return True
    return False

