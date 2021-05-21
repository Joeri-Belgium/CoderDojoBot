import discord
from discord.ext import commands

class Ping(commands.Cog):

    def __init__(self,client):
        self.client = client

    async def embeds(self, ctx, name, value):
        em = discord.Embed(color=ctx.author.color)
        em.add_field(name=name, value=value)
        await ctx.send(embed=em)

    @commands.command(aliases=["latencie", "vertraging", "delay", "latency"],description='Weergeeft de bots ping (vertraging van de bot).')
    async def ping(self, ctx):
        await self.embeds(ctx, "Ping", f"The delay of the bot is: **{round(self.client.latency * 1000)}ms**.")

    @commands.command(aliases=["paf","poef","schoot","fire"],description='some fun command....')
    async def pang(self, ctx):
        await self.embeds(ctx, "PangPangPang",
                          "Alle Indianen... schieten met 🍌🍌🍌...")

    @commands.command(aliases=[],description='some extra fun command...')
    async def pong(self, ctx):
        await self.embeds(ctx, "Pong...",
                          "Ping, pong anyone?")
        
        
        
        
def setup(client):
    client.add_cog(Ping(client))
