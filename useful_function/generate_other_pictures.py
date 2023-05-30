import os
import random
import time

from PIL import Image, ImageDraw, ImageFont
from loader import cursor, connection, bot
from objects_data import *


async def generate_user_profile_photo(user_id: int):
    size = (300, 300)

    user_profile_photo = await bot.get_user_profile_photos(user_id)
    if len(user_profile_photo.photos[0]) > 0:
        file = await bot.get_file(user_profile_photo.photos[0][-1].file_id)
        path = os.path.join(f'images/for_saves/{random.randint(100, 100000000000)}.jpg')
        await bot.download_file(file.file_path, path)
    else:
        path = os.path.join('images/icons/avatar.png')

    def prepare_mask(size_, antialias=2):
        mask = Image.new('L', (size_[0] * antialias, size_[1] * antialias), 0)
        ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
        return mask.resize(size_, Image.ANTIALIAS)

    def crop(im, s):
        w, h = im.size
        k = w / s[0] - h / s[1]
        if k > 0:
            im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
        elif k < 0:
            im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
        return im.resize(s, Image.ANTIALIAS)

    avatar = Image.open(path).convert(mode='RGBA')

    avatar = crop(avatar, size)
    avatar.putalpha(prepare_mask(size, 4))

    frame = Image.open(os.path.join('images/icons/avatar_frame.png'))
    frame.thumbnail((size[0] + 2, size[1] + 2))

    avatar.alpha_composite(frame, (-1, -1))
    os.remove(path)

    return avatar




