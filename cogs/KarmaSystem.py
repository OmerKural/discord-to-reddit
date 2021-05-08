import discord
from discord.ext import commands
from discord.utils import get
import json
import os


class KarmaSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Useful functions
    def add_award(self, guild_id, user_id, award, count):
        """award: 'reddit_silver', 'reddit_gold', 'reddit_platinum'"""
        with open('../karma_data.json') as data_file:
            data = json.load(data_file)
        if not guild_id in data:
            data[guild_id] = {}
        if not user_id in data[guild_id]:
            data[guild_id][user_id] = {}
        if not 'reddit_silver' in data[guild_id][user_id]:
            data[guild_id][user_id]['reddit_silver'] = 0
        if not 'reddit_gold' in data[guild_id][user_id]:
            data[guild_id][user_id]['reddit_gold'] = 0
        if not 'reddit_platinum' in data[guild_id][user_id]:
            data[guild_id][user_id]['reddit_platinum'] = 0
        data[guild_id][user_id][award] += count

    # DONE
    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx):
        """Shows the leaderboard."""
        with open('karma_data.json', 'r') as data_file:
            data = json.load(data_file)
        # Sorts the dict values in descending order.
        clean_ranking_data = {}
        for key, value in data[str(ctx.guild.id)].items():
            for k, v in value.items():
                clean_ranking_data[key] = v
        clean_ranking_data = dict(sorted(clean_ranking_data.items(), reverse=True, key=lambda item: item[1]))
        print(clean_ranking_data)
        ranking_txt = []
        # Shows at max first ten elements of the rankings.
        for user_id in (clean_ranking_data[:10] if len(clean_ranking_data) > 10 else clean_ranking_data):
            username = await self.bot.fetch_user(user_id)
            user_rank = list(clean_ranking_data.keys()).index(user_id) + 1
            if user_rank == 1:
                rank_desc = '🥇  ' + str(username) + ' -> ' + str(clean_ranking_data[user_id])
            elif user_rank == 2:
                rank_desc = '🥈  ' + str(username) + ' -> ' + str(clean_ranking_data[user_id])
            elif user_rank == 3:
                rank_desc = '🥉  ' + str(username) + ' -> ' + str(clean_ranking_data[user_id])
            else:
                rank_desc = '**' + str(user_rank) + '.**  ' + str(username) + ' -> ' + str(clean_ranking_data[user_id])
            ranking_txt.append(str(rank_desc))
        embed = discord.Embed(title="Karma Leaderboard 🏆", description='\n'.join(ranking_txt), color=0xff5600)
        await ctx.send(embed=embed)

    # DONE
    @commands.command(name='mykarma')
    async def karma(self, ctx):
        """Shows your karma count."""
        with open('karma_data.json', 'r') as data_file:
            data = json.load(data_file)
        server_id = str(ctx.guild.id)
        author_id = str(ctx.author.id)
        try:
            await ctx.send(f"You have **{data[server_id][author_id]['karma']}** karma.")
        except KeyError:
            data[server_id][author_id]['karma'] = 0
            await ctx.send(f"You have **{data[server_id][author_id]['karma']}** karma.")

    # todo buy award
    @commands.command(name='buy_award')
    async def buy_award(self, ctx, award):
        "Awards a user's post by substracting karmas from your karma points. (Silver=10, Gold=25, Platinum=50)"
        # Adds custom emojis if it hasn't been done already.
        for filename in os.listdir('./emojis/awards'):
            if filename[:-4] not in [emoji.name for emoji in ctx.guild.emojis]:
                with open(f'./emojis/awards/{filename}', 'rb') as image:
                    await ctx.guild.create_custom_emoji(name=filename[:-4], image=image.read(), roles=[get(ctx.guild.roles, name='shitpost2reddit')])

        # todo market UI
        # Adds the awards to users wallet 'karma_data.json'. (data[guild_id][user_id][award])
        #self.add_award(ctx.guild.id, ctx.user.id, )


def setup(bot):
    bot.add_cog(KarmaSystem(bot))
