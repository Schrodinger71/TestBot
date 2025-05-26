"""
Модуль для запуска бота.
"""

import importlib
import pkgutil
import threading

from bot_init import bot
from config import DISCORD_TOKEN
from web_interface.app import run_web_interface


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
    auto_import_package("web_interface")
    # ...
    # Не забываем подключать
    # новые директории с модуля

    # Запуск веб-интерфейса в отдельном потоке
    web_thread = threading.Thread(target=run_web_interface, daemon=True)
    web_thread.start()

    if DISCORD_TOKEN == "NULL":
        print("[ERROR] Not DISCORD_KEY. Programm Dev-bot shutdown!!")
    else:
        bot.run(DISCORD_TOKEN)
