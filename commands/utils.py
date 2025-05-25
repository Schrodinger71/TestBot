from disnake.ext import commands

import data
from config import FULL_PERMISSION_USERS, GUILD_ID, ROLE_WHITELISTS


def has_any_role_by_keys(*whitelist_keys):
    """
    Декоратор для проверки, имеет ли пользователь одну из указанных ролей по ключам.
    Если пользователь — есть в FULL_PERMISSION_USERS, доступ разрешён всегда.
    При отказе выводятся названия нужных ролей без пинга.
    """

    async def predicate(ctx):
        if ctx.author.id in FULL_PERMISSION_USERS:
            return True

        user_role_ids = [role.id for role in ctx.author.roles]

        # Собираем все разрешённые ID ролей по ключам
        allowed_role_ids = set()
        for key in whitelist_keys:
            allowed_role_ids.update(ROLE_WHITELISTS.get(key, []))

        # Если хотя бы одна из ролей у пользователя есть — пропускаем
        if any(role_id in allowed_role_ids for role_id in user_role_ids):
            return True

        # Если команда выполнена на указанном сервере — показываем имена ролей
        if ctx.guild and ctx.guild.id == GUILD_ID:
            role_names = []
            for role_id in allowed_role_ids:
                role = ctx.guild.get_role(role_id)
                if role:
                    role_names.append(role.name)

            if role_names:
                formatted_roles = ", ".join(f"`{name}`" for name in role_names)
                await ctx.send(
                    f"❌ У вас нет доступа к этой команде.\nТребуемые роли: {formatted_roles}"
                )
            else:
                await ctx.send("❌ У вас нет доступа к этой команде. (Роли не найдены)")
        else:
            await ctx.send("❌ У вас нет доступа к этой команде.")

        return False

    return commands.check(predicate)

def get_user_private_channel(user):
    if user.voice and user.voice.channel and user.voice.channel.id in data.private_channels.values():
        if data.private_channels.get(str(user.id)) == user.voice.channel.id:
            return user.voice.channel
    return None