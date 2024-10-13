import os
from pathlib import Path


class FrontendError(Exception):
    pass


def get_frontend():
    if not os.getenv("frontend"):
        raise FrontendError('Не могу найти "frontend" в переменных среды.')

    frontend = Path(os.getenv("frontend")).absolute()

    if not frontend.exists():
        raise FrontendError(f'Папка "{frontend}" не существует.')
    elif not frontend.is_dir():
        raise FrontendError(f'Путь "{frontend}" не является папкой.')
    elif frontend.name != "dist":
        raise FrontendError('Папка указанная в "frontend" должна иметь название "dist"')

    index = frontend.joinpath("./index.html")

    if not index.exists():
        raise FrontendError(f'Файл "{index}" не найден.')
    elif not index.is_file():
        raise FrontendError(f'"{index}" не является файлом.')
    elif index.is_symlink():
        raise FrontendError(f'"{index}" является ссылкой.')

    assets = frontend.joinpath("./assets/")

    if not assets.exists():
        raise FrontendError(f'Папка "{assets}" не существует.')
    elif not assets.is_dir():
        raise FrontendError(f'"{assets}" не является папкой.')

    return frontend, index, assets
