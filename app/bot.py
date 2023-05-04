import discord
from discord.ext import commands
from birthdaydb import db

# Get the server and channel ids
servers = db.get_servers()
guild_ids = [server[0] for server in servers]
channel_ids = [server[1] for server in servers]
print(channel_ids)

class MyHelpCommand(commands.DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        channel: discord.TextChannel = self.get_destination()
        if str(channel.id) not in channel_ids: # Only answer in the correct channels
            return
        
        return await super().send_bot_help(mapping)

# Init Bot
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=MyHelpCommand())