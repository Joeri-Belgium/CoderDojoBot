import discord
from discord.ext import commands
import os
from keep_alive import keep_alive


intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


@client.command(aliases=["geefninja"])
@commands.has_permissions(ban_members=True)
async def geef_ninja(ctx):
  counter = 0
  role = discord.utils.get(ctx.guild.roles, name="[Ninja]")
  for member in ctx.guild.members:
    if member.top_role == member.roles[0]:
      await member.add_roles(role)
      counter += 1
    else:
      pass
  if counter == 1:
    await ctx.send(f"{counter} member kreeg de role: [Ninja]")
  else:
    await ctx.send(f"{counter} members kregen de role: [Ninja]")  

    
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass

keep_alive()
client.run(os.getenv("token"))
