import discord
from discord.ext import commands
from discord.utils import get
import requests
import json
import os


class KarmaSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # Loads bot_settings
        with open('bot_settings.json', 'r') as settings_file:
            self.settings = json.load(settings_file)
        # Loads karma_data
        with open('karma_data.json', 'r+') as data_file:
            try:
                self.data = json.load(data_file)
                # Deletes duplicate values ( this is not necessary its just my paranoia! )
                with open('karma_data.json', 'w') as data_file:
                    json.dump(self.data, data_file)

            except json.decoder.JSONDecodeError as e:
                self.data = {}
        
    def add_karma(self, guild_id, user_id, count):
        if not guild_id in self.data:
            self.data[guild_id] = {}
        if not user_id in self.data[guild_id]:
            self.data[guild_id][user_id] = 0
        self.data[guild_id][user_id] += count
        with open('karma_data.json', 'r+') as data_file:
            json.dump(self.data, data_file)
        
    def subtract_karma(self, guild_id, user_id, count):
        if not guild_id in self.data:
            self.data[guild_id] = {}
        if not user_id in self.data[guild_id]:
            self.data[guild_id][user_id] = 0
        self.data[guild_id][user_id] -= count
        with open('karma_data.json', 'w') as data_file:
            json.dump(self.data, data_file)

    def is_URL(self, text):
        try:
            response = requests.get(text)
            return True
        except:
            return False
        
    @commands.command(name='setup')
    async def setup(self, ctx, channel: discord.TextChannel):
        "Set the channel for the bot to be active in (the channel must be tagged). Usage: r!setup [channel]"
        # Updates bot_settings accordingly.
        self.settings['CHANNEL_ID'] = str(channel.id)
        with open('bot_settings.json', 'w') as data_file:
            json.dump(self.settings, data_file)
        # Loads bot_settings again.
        with open('bot_settings.json', 'r') as settings_file:
            self.settings = json.load(settings_file)
        await ctx.send(f"**{channel.name}** has been set as reddit channel.")

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx):
        """Shows the leaderboard."""
        with open('karma_data.json', 'r') as data_file:
            data = json.load(data_file)
        # Sorts the dict values in descending order.
        ranking_data = dict(sorted(data[str(ctx.guild.id)].items(), reverse=True, key=lambda item: item[1]))
        ranking_txt = []
        # Shows at max first ten elements of the rankings.
        for user_id in (ranking_data[:10] if len(ranking_data) > 10 else ranking_data):
            username = await self.bot.fetch_user(user_id)
            user_rank = list(ranking_data.keys()).index(user_id) + 1
            if user_rank == 1:
                rank_desc = '🥇  ' + str(username) + ' -> ' + str(ranking_data[user_id])
            elif user_rank == 2:
                rank_desc = '🥈  ' + str(username) + ' -> ' + str(ranking_data[user_id])
            elif user_rank == 3:
                rank_desc = '🥉  ' + str(username) + ' -> ' + str(ranking_data[user_id])
            else:
                rank_desc = '**' + str(user_rank) + '.**  ' + str(username) + ' -> ' + str(ranking_data[user_id])
            ranking_txt.append(str(rank_desc))
        embed = discord.Embed(title="Karma Leaderboard 🏆", description='\n'.join(ranking_txt), color=0xff5600)
        await ctx.send(embed=embed)

    @commands.command(name='mykarma')
    async def mykarma(self, ctx):
        """Shows your karma count."""
        with open('karma_data.json', 'r') as data_file:
            data = json.load(data_file)
        server_id = str(ctx.guild.id)
        author_id = str(ctx.author.id)
        try:
            await ctx.send(f"You have **{data[server_id][author_id]}** karma.")
        except KeyError:
            data[server_id][author_id] = 0
            await ctx.send(f"You have **{data[server_id][author_id]}** karma.")
    
    # Award point system:
    # Silver = +5
    # Gold = +10
    # Platinum = +20
    @commands.command(name='award')
    async def award(self, ctx, award_name):
        """User must have 25 karma points to award a silver, 50 for gold and 100 for platinum. Reply to the message you want to award.
         \nAward name can be: silver, gold, platinum. 
         \nGetting an award adds karma points to your account: 5 for silver, 10 for gold, 20 for platinum."""
        with open('karma_data.json', 'r') as data_file:
            data = json.load(data_file)
            if award_name.lower() == 'silver' and data[str(ctx.guild.id)][str(ctx.author.id)] >= 25:
                await ctx.message.reference.resolved.add_reaction(get(ctx.guild.emojis, name='reddit_silver'))
                self.add_karma(str(ctx.guild.id), str(ctx.message.reference.resolved.author.id), 5)
            elif award_name.lower() == 'gold' and data[str(ctx.guild.id)][str(ctx.author.id)] >= 50:
                await ctx.message.reference.resolved.add_reaction(get(ctx.guild.emojis, name='reddit_gold'))
                self.add_karma(str(ctx.guild.id), str(ctx.message.reference.resolved.author.id), 10)
            elif award_name.lower() == 'platinum' and data[str(ctx.guild.id)][str(ctx.author.id)] >= 100:
                await ctx.message.reference.resolved.add_reaction(get(ctx.guild.emojis, name='reddit_platinum'))
                self.add_karma(str(ctx.guild.id), str(ctx.message.reference.resolved.author.id), 20)

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.channel.id) == self.settings['CHANNEL_ID'] and any([message.attachments, self.is_URL(message.content)]):
            self.add_karma(str(message.guild.id), str(message.author.id), 1)
            # Adds custom emojis if it hasn't been done already.
            for filename in os.listdir('./emojis/reactions'):
                if filename[:-4] not in [emoji.name for emoji in message.guild.emojis]:
                    with open(f'./emojis/reactions/{filename}', 'rb') as image:
                        await message.guild.create_custom_emoji(name=filename[:-4], image=image.read())
            await message.add_reaction(get(message.guild.emojis, name='upvote'))
            await message.add_reaction(get(message.guild.emojis, name='downvote'))
        await self.bot.process_commands(message)


    # Karma point system:
    # Upvote = +1
    # Downvote = -1
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_object = self.bot.get_guild(payload.guild_id)
        channel_object = self.bot.get_channel(payload.channel_id)
        message_object = await channel_object.fetch_message(payload.message_id)
        # Adds custom emojis if it hasn't been done already.
        for filename in os.listdir('./emojis/awards'):
            if filename[:-4] not in [emoji.name for emoji in guild_object.emojis]:
                with open(f'./emojis/awards/{filename}', 'rb') as image:
                    await guild_object.create_custom_emoji(name=filename[:-4], image=image.read(), roles=[get(guild_object.roles, name='discord2reddit')])
        if str(payload.channel_id) == self.settings['CHANNEL_ID']:
            if str(payload.emoji) == str(get(guild_object.emojis, name='upvote')):
                self.add_karma(str(payload.guild_id), str(message_object.author.id), 1)
            if str(payload.emoji) == str(get(guild_object.emojis, name='downvote')):
                self.subtract_karma(str(payload.guild_id), str(message_object.author.id), 1)

            with open('karma_data.json', 'w') as data_file:
                json.dump(self.data, data_file)

    # [ANTI CHEAT] Prevents users from abusing the upvote and downvote buttons spamming them.
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild_object = self.bot.get_guild(payload.guild_id)
        channel_object = self.bot.get_channel(payload.channel_id)
        message_object = await channel_object.fetch_message(payload.message_id)
        if str(payload.channel_id) == self.settings['CHANNEL_ID']:
            if str(payload.emoji) == str(get(guild_object.emojis, name='upvote')):
                self.subtract_karma(str(payload.guild_id), str(message_object.author.id), 1)
            if str(payload.emoji) == str(get(guild_object.emojis, name='downvote')):
                self.add_karma(str(payload.guild_id), str(message_object.author.id), 1)

            with open('karma_data.json', 'w') as data_file:
                json.dump(self.data, data_file)

def setup(bot):
    bot.add_cog(KarmaSystem(bot))