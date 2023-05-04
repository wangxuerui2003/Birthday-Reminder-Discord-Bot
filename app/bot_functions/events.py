from bot import bot
from .background_tasks import *

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}!")
    background_check_birthday.start()
    background_delete_expired_threads.start()
    check_guilds.start()


@bot.event
async def on_command_error(ctx: commands.context.Context, error):
    if str(ctx.channel.id) not in channel_ids:
        return

    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("Command not found.")


@bot.event
async def on_guild_join(guild: discord.Guild):
    await service_in_new_server(guild, db)


@bot.event
async def on_guild_remove(guild: discord.Guild):
    db.delete_removed_servers_and_birthdays(guild.id)