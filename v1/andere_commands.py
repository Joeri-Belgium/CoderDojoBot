import discord
from discord.ext import commands
import os
from keep_alive import keep_alive


intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".help"))


@client.event
async def on_member_join(member):
    em = discord.Embed(title=None, color=discord.Color.blue())
    em.add_field(name="Welkom!", value=f"Welkom bij de **CoderDojo Discord** server, {member.name}! Dit is de plek waar "
    f"je je vragen kunt stellen over code gerelateerde zaken!\n\n Om van start te "
    f"gaan moet je even een korte **vragenlijst** invullen in "
    f"#introductie.\n\nGelieve de **regels** van de server te volgen, die kun je "
    f"terugvinden in #regels.\n\nAls je nog niet zo goed begrijpt hoe Discord "
    f"werkt staat er in #hoe-discord-gebruiken een **tutorial**.\n\nAls je problemen "
    f"ervaart met de server maak dan een **ticket** aan, dit kan je doen door in "
    f"#maak-ticket, door te klikken op het emoticon onder het bericht.\n\n**Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.**")
    await member.send(embed=em)

@client.command(aliases=["membercount", "members", "member"])
async def member_count(ctx):
  member_verified = 0
  member_count = 0
  bot_counter = 0
  online_bots = 0
  for member in ctx.guild.members:
      if not member.bot:
        member_count += 1
        for role in member.roles:
          if role.name == "[Ninja]" or role.name == "[Coach]":
              member_verified += 1
      else:
          bot_counter += 1
          if str(member.status) != "offline":
            online_bots += 1
  em = discord.Embed(title=None, color=ctx.author.color)
  em.add_field(name="Members & Bots", value=f"**Members:** {member_count}\nㅤ*Geveerifeerd:* {member_verified}\nㅤNiet *geveerifeerd:*  {member_count - member_verified}\n**Bots:** {bot_counter}\nㅤ*Online:* {online_bots}\nㅤ*Offline:* {bot_counter - online_bots}")
  await ctx.send(embed=em)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass



keep_alive()
client.run(os.getenv("token"))
