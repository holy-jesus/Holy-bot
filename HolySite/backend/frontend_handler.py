import os
from pathlib import Path

from fastapi.responses import HTMLResponse


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


frontend_path, index_path, assets_path = get_frontend()


def get_frontend():
    return HTMLResponse(index_path.read_text("utf-8"))
