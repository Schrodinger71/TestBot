"""
Этот модуль содержит все основные конфигурации Dev-bot.
"""

import os

from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()


def get_env_variable(name: str, default: str = "NULL") -> str:
    """
    Функция для безопасного получения переменных окружения.
    Если переменная не найдена, возвращает значение по умолчанию.
    """
    value = os.getenv(name)
    if not value:
        print(
            f"Предупреждение: {name} не найден в файле .env. "
            f"Используется значение по умолчанию: {default}"
        )
        return default
    return value


# Получение переменных из окружения
DISCORD_TOKEN = get_env_variable("DISCORD_TOKEN")
GIT_PAT_TOKEN = get_env_variable("GIT_PAT_TOKEN")
USER_WEB = get_env_variable("USER_WEB")
PASSWORD_WEB = get_env_variable("PASSWORD_WEB")

LOG_TECH_CHANNEL = 1376098205997076561  # ID канала с логами
BACKUP_CHANNEL_ID = 1376098306043674745 # ID канала для сохранения настроек в случае отключения
GUILD_ID = 783394066691260438          # ID Discord сервера
SHUTDOWN_TIMER = 5 * 60 * 60 + 56       # Время 5ч 56мин, время работы бота, после чего будет рестарт

AUTHOR = 'Schrodinger71'
REPO = 'TestBot'

# Айди пользователей с полными правами ко всем командам бота
FULL_PERMISSION_USERS = [328502766622474240]

# Ключи айди ролей, для распределения доступов к командам (Взяты рандомные айди для примера)
ROLE_WHITELISTS = {
    # Ключи ID ролей для вайтлистов
    "head_project": [
        1374393293646860419, # [👑] Высшее руководство
    ],
    "whitelist_role_id": [
        1060191651538145420,
        1347877224430436493,
        # Чисто пример
    ],
    "minor_role_id": [
        1347877224430436493,
        1060264704838209586,
        1054908932868538449,
        1054827766211694593,
        1127152229439246468,
        1266161300036390913,
    ],
}
