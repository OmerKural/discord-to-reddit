import discord
from discord.ext import commands
from discord.utils import get
import os
import json
import requests

bot = commands.Bot(command_prefix='r!')

# Loads Cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(filename, "loaded.")

# Loads bot_settings
with open('bot_settings.json', 'r') as settings_file:
    settings = json.load(settings_file)

# Loads karma_data
with open('karma_data.json', 'r+') as data_file:
    try:
        data = json.load(data_file)
        # Deletes duplicate values ( this is not necessary its just my paranoia! )
        with open('karma_data.json', 'w') as data_file:
            json.dump(data, data_file)

    except json.decoder.JSONDecodeError as e:
        data = {}

# Useful functions
def add_karma(guild_id, user_id, count):
    if not guild_id in data:
        data[guild_id] = {}
    if not user_id in data[guild_id]:
        data[guild_id][user_id] = {}
    if not 'karma' in data[guild_id][user_id]:
        data[guild_id][user_id]['karma'] = 0
    data[guild_id][user_id]['karma'] += count

def subtract_karma(guild_id, user_id, count):
    if not guild_id in data:
        data[guild_id] = {}
    if not user_id in data[guild_id]:
        data[guild_id][user_id] = {}
    if not 'karma' in data[guild_id][user_id]:
        data[guild_id][user_id]['karma'] = 0
    data[guild_id][user_id]['karma'] -= count

def is_URL(text):
    try:
        response = requests.get(text)
        return True
    except:
        return False


# Runs Bot
@bot.event
async def on_ready():
    print('Bot is running...')


@bot.event
async def on_message(message):
    if str(message.channel.id) == settings['CHANNEL_ID'] and any([message.attachments, is_URL(message.content)]):
        add_karma(str(message.guild.id), str(message.author.id), 1)
        # Adds custom emojis if it hasn't been done already.
        for filename in os.listdir('./emojis/reactions'):
            if filename[:-4] not in [emoji.name for emoji in message.guild.emojis]:
                with open(f'./emojis/reactions/{filename}', 'rb') as image:
                    await message.guild.create_custom_emoji(name=filename[:-4], image=image.read())
        await message.add_reaction(get(message.guild.emojis, name='upvote'))
        await message.add_reaction(get(message.guild.emojis, name='downvote'))
    await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction, user):
    print(str(reaction))
    print(get(reaction.message.guild.emojis, name='upvote'))
    if str(reaction.message.channel.id) == settings['CHANNEL_ID']:
        if str(reaction) == str(get(reaction.message.guild.emojis, name='upvote')):
            add_karma(str(reaction.message.guild.id), str(reaction.message.author.id), 1)
        if str(reaction) == str(get(reaction.message.guild.emojis, name='downvote')):
            subtract_karma(str(reaction.message.guild.id), str(reaction.message.author.id), 1)

        with open('karma_data.json', 'w') as data_file:
            json.dump(data, data_file)


@bot.command(name='setup')
async def setup(ctx, channel: discord.TextChannel):
    "Set the channel for the bot to be active in (the channel must be tagged). Usage: r!setup [channel]"
    settings['CHANNEL_ID'] = str(channel.id)
    with open('bot_settings.json', 'w') as data_file:
        json.dump(settings, data_file)
    await ctx.send(f"**{channel.name}** has been set as reddit channel.")


bot.run(settings['TOKEN'])
