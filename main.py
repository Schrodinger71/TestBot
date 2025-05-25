"""
Модуль для запуска бота.
"""

import importlib
import pkgutil

from bot_init import bot
from config import DISCORD_TOKEN


def auto_import_package(package_name: str):
    """Автоматически импортирует все модули внутри пакета"""
    package = importlib.import_module(package_name)
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        importlib.import_module(f"{package_name}.{module_name}")


if __name__ == "__main__":
    # Автоматический импорт подмодулей
    auto_import_package("commands")
    auto_import_package("events")
    auto_import_package("modules")
    auto_import_package("tasks")
    # ...
    # Не забываем подключать
    # новые директории с модуля

    if DISCORD_TOKEN == "NULL":
        print("[ERROR] Not DISCORD_KEY. Programm Dev-bot shutdown!!")
    else:
        bot.run(DISCORD_TOKEN)
