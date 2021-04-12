import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")

async def role_controle(ctx, role_naam):
  role = discord.utils.get(ctx.guild.roles, name=role_naam)
  embed = discord.Embed(title=None, color=ctx.author.color)
  if role in ctx.author.roles:
    embed.add_field(name="Role aangepast", value=f"{role_naam} is verwijdert")
    await ctx.author.remove_roles(role)
    await ctx.send(embed=embed)
  else:
    embed.add_field(name="Role aangepast", value=f"{role_naam} is toegevoegd")
    await ctx.author.add_roles(role)
    await ctx.send(embed=embed)


@client.command()
async def leuven(ctx):
  await role_controle(ctx, "[Dojo Leuven]")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass

keep_alive()
client.run(os.getenv("token"))
