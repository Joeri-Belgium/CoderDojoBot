import discord
from discord.ext import commands

class Help(commands.Cog):

    def __init__(self,client):
        self.client = client

    async def embeds(self, ctx, name, value):
        em = discord.Embed(color=ctx.author.color)
        em.add_field(name=name, value=value)
        await ctx.send(embed=em)

    @commands.command(aliases=["help2"])
    async def help(self, ctx, arg1):
        for command in self.client.walk_commands():
            if hasattr(command, 'description'):
                print(command.name)
                if command.name == arg1:
                  await self.embeds(ctx, command,command.description)

def setup(client):
    client.add_cog(Help(client))