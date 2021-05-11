import discord
from discord.ext import commands
import os
import json

bot = commands.Bot(command_prefix='r!')

# Loads Cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(filename, "loaded.")

# Loads bot_settings
with open('bot_settings.json', 'r') as settings_file:
    settings = json.load(settings_file)

# Runs Bot
@bot.event
async def on_ready():
    print('Bot is running...')




bot.run(settings['TOKEN'])
