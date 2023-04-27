import discord
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Modal, TextInput
import datetime
import dotenv
from pathlib import Path
import os
import certifi
import asyncio

os.environ["SSL_CERT_FILE"] = certifi.where()

dotenv.load_dotenv(Path('../.env'))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


class BirthdayModal(Modal, title="Birthday Reminder"):
    answer = TextInput(
        label="Enter your birthday (dd/mm/yyyy) | (Enter 0000 for anonymous birthyear)",
        style=discord.TextStyle.short,
        placeholder="21/11/2003",
        required=True,
        max_length=10,
        min_length=10
    )

    async def on_submit(self, interaction: Interaction[ClientT]) -> Coroutine[Any, Any, None]:
        return await super().on_submit(interaction)


@bot.command()
async def set_birthday(ctx):
    def check(message):
        try:
            birthday = datetime.datetime.strptime(message.content, '%m/%d/%Y')
            return True
        except Exception as e:
            print(e)
            return False

    # text_input = TextInput(label="birthday")
    # await ctx.send('Plase enter some text:')
    # input_msg = await ctx.send(embed=discord.Embed(title="Enter some text:"))
    # try:
    #     input_text = await bot.wait_for('message', check=check, timeout=30)
    #     await input_msg.delete()
    #     await input_text.reply(f'You entered: {input_text.content}')
    # except asyncio.TimeoutError:
    #     await input_msg.delete()
    #     await ctx.send('You took too long to enter text.')

bot.run(os.getenv('TOKEN'))
