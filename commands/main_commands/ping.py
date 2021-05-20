import discord
from discord.ext import commands

class Ping(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.client.__names__ = 'ping'
        self.description = "Weergeeft de bots ping (vertraging van de bot)."

    async def embeds(self, ctx, name, value):
        em = discord.Embed(color=ctx.author.color)
        em.add_field(name=name, value=value)
        await ctx.send(embed=em)

    @commands.command(aliases=["latencie", "vertraging", "delay", "latency"],description='Weergeeft de bots ping (vertraging van de bot).')
    async def ping(self, ctx):
        await self.embeds(ctx, "Ping", f"The delay of the bot is: **{round(self.client.latency * 1000)}ms**.")

def setup(client):
    client.add_cog(Ping(client))