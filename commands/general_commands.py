"""
Модуль предназначенный для общих комманд бота
"""

import asyncio
import os
import platform
import socket
import sys
from datetime import datetime

import psutil
from disnake import AppCommandInteraction, Embed

from bot_init import bot
from config import FULL_PERMISSION_USERS
from events.on_slash_command import log_slash_command
from tasks.shutdown_timer import shutdown_procces


@bot.slash_command(name="help", description="Показать список доступных команд.")
@log_slash_command
async def help_command(interaction: AppCommandInteraction):
    """
    Команда для отображения списка команд в стиле консольного интерфейса проекта 'Дельта'.
    """
    if interaction.author.id in FULL_PERMISSION_USERS:
        perm_user = "Супер-пользователь"
    else:
        perm_user = "Пользователь"

    embed = Embed(
        title="🧭 ANAGIRIUM CONSOLE INTERFACE",
        description=(
            "📡 **Сессия установлена**\n"
            f"🔒 Уровень доступа: `{perm_user}`\n"
            "⌘ Введите команду для выполнения операции.\n"
            "‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
            "⚙️ **Основные команды:**\n"
            "  • `/ping` — Проверка связи с ядром\n"
            "  • `/systeminfo` — Системные показатели\n"
            "  • `/shutdown` — Завершение работы ядра. Только супер пользователю\n"
            "\n"
            "🎙️ **Управление приватными голосовыми каналами:**\n"
            "  • `/lock` — Закрыть канал для других\n"
            "  • `/unlock` — Открыть канал для других\n"
            "  • `/name <имя>` — Переименовать канал\n"
            "  • `/limit <число>` — Установить лимит участников (0 — без лимита)\n"
            "  • `/bitrate <число>` — Изменить битрейт канала\n"
            "  • `/permit <пользователь>` — Разрешить доступ пользователю\n"
            "  • `/reject <пользователь>` — Запретить доступ и выгнать из канала\n"
            "\n"
            "🔔 **Администрирование триггер-каналов:**\n"
            "  • `/add_trigger_channel <канал> <тег>` — Добавить триггер-канал\n"
            "  • `/remove_trigger_channel <канал>` — Удалить триггер-канал\n"
            "  • `/list_trigger_channels` — Показать список триггер-каналов\n"
            "\n"
            "📎 Используйте `/` для вызова автозаполнения.\n"
            "⌛ Ожидание ввода новой команды..."
        ),
        color=0x2f3136  # Тёмный цвет в стиле терминала
    )

    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/1374507045058773042/1375386558101979146/Anagiri2.jpg?ex=6831800c&is=68302e8c&hm=3b8261b295778020728b483837ea2b0c0ae8a8979472a5c46be8dd3d9728a9ae&=&format=webp"
    )

    embed.set_footer(text="AnagiriumBot — AI Unit [D-∆] | Проект 'Дельта'")

    await interaction.response.send_message(embed=embed)


@bot.command(name="ping", help="Проверяет задержку бота.")
async def ping(ctx):
    """
    Команда для проверки задержки бота.
    """

    latency = round(bot.latency * 1000)
    emoji = "🏓" if latency < 100 else "🐢"
    await ctx.send(f"{emoji} Pong! Задержка: **{latency}ms**")

@bot.slash_command(name="ping", help="Проверяет задержку бота.")
@log_slash_command
async def ping_command(interaction: AppCommandInteraction):
    """
    Команда для проверки задержки бота.
    """

    latency = round(bot.latency * 1000)
    emoji = "🏓" if latency < 100 else "🐢"
    await interaction.response.send_message(f"{emoji} Pong! Задержка: **{latency}ms**")


@bot.slash_command(name="shutdown", description="Аварийное отключение ядра ANAGIRIUM.")
async def shutdown(interaction: AppCommandInteraction):
    if interaction.author.id not in FULL_PERMISSION_USERS:
        await interaction.response.send_message(
            "```ansi\n[ОТКАЗ] :: У вас нет доступа к отключению ядра.\n> Запрос отклонён.\n```"
        )
        return

    await interaction.response.send_message("```ansi\n[ANAGIRIUM NODE] :: CORE SHUTDOWN INITIATED\n```")
    message = await interaction.original_message()

    steps = [
        "> Завершение всех процессов...",
        "> Закрытие протоколов связи...",
        "> Отключение AI-модуля...",
        "> Уничтожение временных переменных...",
        "> Сессия окончена. До связи.",
    ]

    content = "```ansi\n[ANAGIRIUM NODE] :: CORE SHUTDOWN INITIATED\n"
    for step in steps:
        await asyncio.sleep(0.7)
        content += step + "\n"
        await message.edit(content=content + "```")

    await asyncio.sleep(1)
    await shutdown_procces()


@bot.slash_command(name="systeminfo", description="Выводит информацию о системе в SCP-консольном стиле.")
@log_slash_command
async def systeminfo(interaction: AppCommandInteraction):
    await interaction.response.send_message("```ansi\n[ANAGIRIUM NODE] :: SYSTEM DIAGNOSTICS INITIATED...\n```")
    message = await interaction.original_message()

    uname = platform.uname()
    os_name = f"{uname.system} {uname.release}"
    architecture = uname.machine
    processor = uname.processor or platform.processor()
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    cpu_cores = os.cpu_count() or "Неизвестно"

    # RAM
    total_ram = "Неизвестно"
    if os.name == "posix":
        try:
            with open('/proc/meminfo') as f:
                meminfo = f.read()
            mem_kb = int([line for line in meminfo.split('\n') if "MemTotal" in line][0].split()[1])
            total_ram = f"{round(mem_kb / (1024 ** 2), 2)} GB"
        except:
            pass
    elif os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong),
                            ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),]
            mem_status = MEMORYSTATUSEX()
            mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))
            total_ram = f"{round(mem_status.ullTotalPhys / (1024 ** 3), 2)} GB"
        except:
            pass

    lines = [
        "[ANAGIRIUM NODE] :: SYSTEM DIAGNOSTICS REPORT",
        "──────────────────────────────────────────────",
        f"> Hostname        :: {hostname}",
        f"> OS              :: {os_name}",
        f"> Architecture    :: {architecture}",
        f"> Processor       :: {processor}",
        f"> IP Address      :: {ip_address}",
        f"> CPU Cores       :: {cpu_cores}",
        f"> RAM Total       :: {total_ram}",
        "──────────────────────────────────────────────",
        f"> Status          :: STABLE",
        f"> Last Update     :: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
    ]

    full_text = "```ansi\n"
    for line in lines:
        full_text += line + "\n"
        await asyncio.sleep(0.7)
        await message.edit(content=full_text + "```")
