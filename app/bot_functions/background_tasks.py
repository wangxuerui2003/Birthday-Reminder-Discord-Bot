from discord.ext import tasks
from helpers import *
from bot import channel_ids, guild_ids

# Init last check to yesterday
last_birthday_check: datetime.date = datetime.date.today() - datetime.timedelta(days=1)

@tasks.loop(hours=1)
async def background_check_birthday():
    global last_birthday_check

    if last_birthday_check == datetime.date.today() - datetime.timedelta(days=1):  # If last check is yesterday
        last_birthday_check = datetime.date.today() # Change last check to today

        birthdays: List[tuple] = db.get_birthdays()
        channels = [bot.get_channel(int(channel_id)) for channel_id in channel_ids]

        await check_birthday(birthdays, channels)


@tasks.loop(hours=6)
async def background_delete_expired_threads():
    birthdays: List[tuple] = db.get_birthdays()
    channels = [bot.get_channel(int(channel_id)) for channel_id in channel_ids]
    await delete_expired_threads(birthdays, channels)


@tasks.loop(minutes=10)
async def check_guilds():
    global guild_ids

    current_guilds = [guild for guild in bot.guilds]
    current_guild_ids = [str(guild.id) for guild in current_guilds]

    new_guilds = [guild for guild in current_guilds if str(guild.id) not in guild_ids]
    if new_guilds:
        for guild in new_guilds:
            await service_in_new_server(guild, db)

    removed_guild_ids = set(guild_ids) - set(current_guild_ids)
    if removed_guild_ids:
        for guild_id in removed_guild_ids:
            db.delete_removed_servers_and_birthdays(guild_id)
        guild_ids = current_guild_ids