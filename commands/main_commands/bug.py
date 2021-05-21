import discord
from discord.ext import commands

class Bug(commands.Cog):

    def __init__(self,client):
        self.client = client

    async def embeds(self, ctx, name, value):
        em = discord.Embed(color=ctx.author.color)
        em.add_field(name=name, value=value)
        await ctx.send(embed=em)

    @commands.command()
    async def bug(self, ctx):
        await self.embeds(ctx, "Bug gevonden?", "Stuur een bericht naar beastmatser#0728 om de bug te reporten.")

def setup(client):
    client.add_cog(Bug(client))