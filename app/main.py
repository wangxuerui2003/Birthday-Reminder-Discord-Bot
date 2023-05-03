import discord
from discord.ext import commands, tasks
from discord.interactions import Interaction
from discord.ui import Modal, TextInput, Button, View
import datetime
import dotenv
import sys
import os
import certifi
from typing import Any, Coroutine, List, Mapping, Optional

from birthdaydb import BirthdayDB
from BirthdayModal import BirthdayModal
from helpers import *
from get_happybirthday_meme import get_random_birthday_meme


# Validate ssl certificate
os.environ["SSL_CERT_FILE"] = certifi.where()

# Load environment variables in the .env file
dotenv.load_dotenv()

# Init DB
db = BirthdayDB()
if not db.db_conn_success:
    print("Can't connect to the database!", file=sys.stderr)
    sys.exit()

# Get the server and channel ids
servers = db.get_servers()
guild_ids = [server[0] for server in servers]
channel_ids = [server[1] for server in servers]


class MyHelpCommand(commands.DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        channel: discord.TextChannel = self.get_destination()
        if channel.id not in channel_ids: # Only answer in the correct channels
            return
        
        return await super().send_bot_help(mapping)


# Init Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=MyHelpCommand())


@bot.command()
@channels_only(channel_ids)
async def set_birthday(ctx: commands.context.Context):
    """
        Set your birthday, only once for each user.
    """
    
    async def send_modal_callback(interaction: Interaction):
        await interaction.response.send_modal(BirthdayModal())
    
    button = Button(label="Click me!", custom_id="my_button", style=discord.ButtonStyle.green)
    button.callback = send_modal_callback
    view = View()
    view.add_item(button)
    await ctx.send(view=view)


@bot.command()
@channels_only(channel_ids)
async def list_birthdays(ctx: commands.context.Context):
    """
        List all recorded birthdays.
    """

    list_of_birthdays = ""
    birthdays = db.get_birthdays()

    if not birthdays:
        return
    
    for user_id, username, birthday in birthdays:
        user = await bot.fetch_user(int(user_id))
        list_of_birthdays += f"User \"{user.name}\": {username}'s birthday is on {str(birthday.day).zfill(2)}/{str(birthday.month).zfill(2)}\n"

    if list_of_birthdays != "":
        await ctx.send(list_of_birthdays)


async def check_birthday(birthdays, channels) -> Coroutine: #todo
    """
        Check all the birthdays for birthday today and tomorrow.
    """

    for user_id, username, birthday, server_id in birthdays:
        channel = db.get_channelid_in_server(db, server_id)
        if today_birthday(birthday):
            user = await bot.fetch_user(int(user_id))
            message = await channel.send(f"Happy Birthday {username}! {user.mention}")
            meme_url = get_random_birthday_meme()
            if meme_url:
                embed_meme = discord.Embed(title="Happy Birthday!")
                embed_meme.set_image(url=meme_url)
                await channel.send(embed=embed_meme)
            await create_thread(message, username)
        elif tmr_birthday(birthday):
            user = await bot.fetch_user(int(user_id))
            message = await channel.send(f"Rememeber tomorrow is your birthday {username}! {user.mention}")
            await create_thread(message, username)


@tasks.loop(hours=1)
async def background_check_birthday():
    global last_birthday_check

    if last_birthday_check == datetime.date.today() - datetime.timedelta(days=1):  # If last check is yesterday
        last_birthday_check = datetime.date.today() # Change last check to today

        birthdays: List[tuple] = db.get_birthdays()
        channels = [bot.get_channel(channel_id) for channel_id in channel_ids]
        await delete_expired_threads(birthdays, channels)

        await check_birthday(birthdays, channels)


@tasks.loop(hours=6)
async def background_delete_expired_threads():
    birthdays: List[tuple] = db.get_birthdays()
    channels = [bot.get_channel(channel_id) for channel_id in channel_ids]
    await delete_expired_threads(birthdays, channels)


@tasks.loop(minutes=10)
async def check_guilds():
    global guild_ids

    current_guilds = [guild for guild in bot.guilds]
    current_guild_ids = [guild.id for guild in current_guilds]

    new_guilds = [guild for guild in current_guilds if guild.id not in guild_ids]
    if new_guilds:
        for guild in new_guilds:
            await service_in_new_server(guild, db, bot)

    removed_guild_ids = set(guild_ids) - set(current_guild_ids)
    if removed_guild_ids:
        for guild_id in removed_guild_ids:
            db.delete_removed_servers_and_birthdays(guild_id)
        guild_ids = current_guild_ids

@bot.command()
async def check_permissions(ctx):
    member = ctx.guild.get_member(bot.user.id)
    permissions = member.guild_permissions
    if permissions.manage_channels:
        await ctx.send("I have permission to manage channels.")
    else:
        await ctx.send("I do not have permission to manage channels.")

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}!")
    background_check_birthday.start()
    background_delete_expired_threads.start()
    check_guilds.start()


@bot.event
async def on_command_error(ctx: commands.context.Context, error):
    if ctx.channel.id not in channel_ids:
        return

    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("Command not found.")


@bot.event
async def on_guild_join(guild: discord.Guild):
    await service_in_new_server(guild, db, bot)


@bot.event
async def on_guild_remove(guild: discord.Guild):
    db.delete_removed_servers_and_birthdays(guild.id)


bot.run(os.getenv('TOKEN'))
