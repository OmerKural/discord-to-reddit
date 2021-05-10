import discord
from discord.ext import commands
from discord.utils import get
import json
import os


class KarmaSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # DONE
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

    # DONE
    @commands.command(name='mykarma')
    async def karma(self, ctx):
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

    # Condition: User must have 25 karma points to use silver, 50 for gold and 100 for platinum.
    @commands.command(name='award')
    async def award(self, ctx, award_name):
        """User must have 25 karma points to award a silver, 50 for gold and 100 for platinum. Reply to the message you want to award.
         \nAward name can be: silver, gold, platinum"""
        with open('karma_data.json', 'r') as data_file:
            data = json.load(data_file)
            if award_name.lower() == 'silver' and data[str(ctx.guild.id)][str(ctx.author.id)] >= 25:
                await ctx.message.reference.resolved.add_reaction(get(ctx.guild.emojis, name='reddit_silver'))
            elif award_name.lower() == 'gold' and data[str(ctx.guild.id)][str(ctx.author.id)] >= 50:
                await ctx.message.reference.resolved.add_reaction(get(ctx.guild.emojis, name='reddit_gold'))
            elif award_name.lower() == 'platinum' and data[str(ctx.guild.id)][str(ctx.author.id)] >= 100:
                await ctx.message.reference.resolved.add_reaction(get(ctx.guild.emojis, name='reddit_platinum'))
        
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_object = self.bot.get_guild(payload.guild_id)
        # Adds custom emojis if it hasn't been done already.
        for filename in os.listdir('./emojis/awards'):
            if filename[:-4] not in [emoji.name for emoji in guild_object.emojis]:
                with open(f'./emojis/awards/{filename}', 'rb') as image:
                    await guild_object.create_custom_emoji(name=filename[:-4], image=image.read(), roles=[get(guild_object.roles, name='discord2reddit')])


def setup(bot):
    bot.add_cog(KarmaSystem(bot))