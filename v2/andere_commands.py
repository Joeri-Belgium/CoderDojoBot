import discord
from discord.ext import commands
from keep_alive import keep_alive
import os

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=".help"))


@client.event
async def on_member_join(member):
    em = discord.Embed(title=None, color=discord.Color.blue())
    introductie_channel = client.get_channel(829633531579203595)
    regels_channel = client.get_channel(790536868236099604)
    hoe_discord_channel = client.get_channel(788694027359748106)
    ticket_channel = client.get_channel(788696271720415242)
    em.add_field(name="Welkom!", value=f"Welkom bij de **CoderDojo Discord** server, {member.name}! Dit is de plek waar "
    f"je je vragen kunt stellen over code gerelateerde zaken!\n\n Om van start te "
    f"gaan moet je even een korte **vragenlijst** invullen in "
    f"{introductie_channel.mention}.\n\nGelieve de **regels** van de server te volgen, die kun je "
    f"terugvinden in {regels_channel.mention}.\n\nAls je nog niet zo goed begrijpt hoe Discord "
    f"werkt staat er in {hoe_discord_channel.mention} een **tutorial**.\n\nAls je problemen "
    f"ervaart met de server maak dan een **ticket** aan, dit kan je doen door in "
    f"{ticket_channel.mention}, door te klikken op het emoticon onder het bericht.\n\n**Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.**")
    await member.send(embed=em)

@client.command(aliases=["membercount", "members", "member"])
async def member_count(ctx):
  online_bots = len([str(member.status) for member in ctx.guild.members if member.bot and str(member.status) != 'offline'])
  offline_bots = len([str(member.status) for member in ctx.guild.members if member.bot and str(member.status) == 'offline'])
  verified_members = len([member.name for member in ctx.guild.members if "[Coach]" in [role.name for role in member.roles] or "[Ninja]" in [role.name for role in member.roles]])
  unverified_members = len(ctx.guild.members) - online_bots - offline_bots - verified_members
  embed = discord.Embed(color=ctx.author.color)
  embed.add_field(name="Members:", value=f"```Geveerifeerd: {verified_members}```\n```Niet geveerifeerd: {unverified_members}```")
  embed.add_field(name="Bots:", value=f"```Online bots: {online_bots}```\n```Offline bots: {offline_bots}```")
  await ctx.send(embed=embed)
  
@client.command()
async def sessie(ctx):
  def check1(m):
    return m.channel == ctx.channel and m.author == ctx.author
  def check2(payload):
    if msg.id == payload.message_id and payload.user_id != 808736566213345281 and discord.utils.get(payload.member.roles, name="[Moderator]") in payload.member.roles:
      return True
  await ctx.send("Wat is de naam van je sessie?")
  sessie_naam = await client.wait_for('message', check=check1, timeout=180)
  await ctx.send("Wanneer gaat de sessie door?")
  sessie_datum = await client.wait_for('message', check=check1, timeout=180)
  await ctx.send("Een kleine beschrijving van de sessie:")
  sessie_beschrijving = await client.wait_for('message', check=check1, timeout=600)
  embed = discord.Embed(title=sessie_naam.content, color=discord.Colour.blurple())
  embed.add_field(name="Datum", value=f"`{sessie_datum.content}`")
  embed.add_field(name="Beschrijving:", value=f"```{sessie_beschrijving.content}```", inline=False)
  msg = await client.get_channel(832263662566637640).send(embed=embed)
  await msg.add_reaction("✔")
  await client.wait_for("raw_reaction_add", check=check2)
  embed.set_footer(text="Deze sessie is afgelopen!")
  await msg.clear_reactions()
  await msg.edit(embed=embed)
  
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass

keep_alive()
client.run(os.environ['token'])
