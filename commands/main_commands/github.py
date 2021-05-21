import discord
from discord.ext import commands

class Github(commands.Cog):

    def __init__(self,client):
        self.client = client

    async def embeds(self, ctx, name, value):
        em = discord.Embed(color=ctx.author.color)
        em.add_field(name=name, value=value)
        await ctx.send(embed=em)

    @commands.command()
    async def github(self, ctx):
        await self.embeds(ctx, "Github", "De code van de CoderDojo Discord is terug te vinden op: https://github.com/beastmatser3/CoderDojoBot")

def setup(client):
    client.add_cog(Github(client))