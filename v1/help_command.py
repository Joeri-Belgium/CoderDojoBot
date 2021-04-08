import discord
from discord.ext import commands
import os
from keep_alive import keep_alive


def embeds(ctx, title, name, value):
    em = discord.Embed(title=title, color=ctx.author.color)
    em.add_field(name=name, value=value)
    return em


intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


@client.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title="Commands", description="Typ .help <command> voor meer informatie over die command.",
                       color=ctx.author.color)
    em.add_field(name="**Ping**", value="Weergeeft de bots ping (vertraging van de bot).", inline=False)
    em.add_field(name="**Python**", value="Status van de python-programmeurs.", inline=False)
    em.add_field(name="**Sratch**", value="Status van de scratch-programmeurs.", inline=False)
    em.add_field(name="**Webdesigner**", value="Status van de webdesigners.", inline=False)
    em.add_field(name="**Java**", value="Status van de java-programmeurs.", inline=False)
    em.add_field(name="**3D-Modelers**", value="Status van de 3D-modelers.", inline=False)
    em.add_field(name="**Maker**", value="Status van de makers.", inline=False)
    em.add_field(name="**Game-Dev**", value="Status van de game-devs.", inline=False)
    em.add_field(name="**C**", value="Status van de c-programmeurs.", inline=False)
    em.add_field(name="**Ninja**", value="Status van de ninja's", inline=False)
    em.add_field(name="**Coach**", value="Status van de coaches.", inline=False)
    em.add_field(name="**Moderators  on trail**", value="Status van de moderators on trail.", inline=False)
    em.add_field(name="**Moderators**", value="Status van de moderators.", inline=False)
    em.add_field(name="**Membercount**", value="Weergeeft het aantal bots en members.", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["py"])
async def python(ctx):
    em = embeds(ctx, None, "Python", "Status van de python-programmeurs.")
    em.add_field(name="Aliassen", value=".python, .py", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=[])
async def scratch(ctx):
    em = embeds(ctx, None, "Scratch", "Status van de scratch-programmeurs.")
    em.add_field(name="Aliassen", value=".scratch", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["web", "webdesign"])
async def webdesigner(ctx):
    em = embeds(ctx, None, "Webdesigner", "Status van de webdesigners.")
    em.add_field(name="Aliassen", value=".web, .webdesigner, .webdesign", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["javadev", "java-dev", "js"])
async def java(ctx):
    em = embeds(ctx, None, "Java", "Status van de java-programmeurs.")
    em.add_field(name="Aliassen", value=".java, .js", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["3D", "3d", "3D-Modelers", "3D-Modeler", "3D-modeler", "3D-modelers"])
async def d3(ctx):
    em = embeds(ctx, None, "3D-Modelers", "Status van de 3D-Modelers.")
    em.add_field(name="Aliassen", value=".3d, .3D, .3D-Modelers, .3D-Modeler, 3D-modeler, .3D-modelers", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["makers"])
async def maker(ctx):
    em = embeds(ctx, None, "Maker", "Status van de makers.")
    em.add_field(name="Aliassen", value=".maker, .makers", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["game-dev", "gamedev", "game"])
async def game_dev(ctx):
    em = embeds(ctx, None, "Game-Dev", "Status van de game-devs")
    em.add_field(name="Aliassen", value=".gamedev, .game-dev, .game", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=[])
async def c(ctx):
    em = embeds(ctx, None, "C", "Status van de c-programmeurs.")
    em.add_field(name="Aliassen", value=".c", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["modsontrail"])
async def modontrail(ctx):
    em = embeds(ctx, None, "Moderator on trail", "Status van de moderators on trail.")
    em.add_field(name="Aliassen", value=".modontrail, .modsontrail", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["coaches"])
async def coach(ctx):
    em = embeds(ctx, None, "Coach", "Status van de coaches.")
    em.add_field(name="Aliassen", value=".coach, .coaches", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=[])
async def ninja(ctx):
    em = embeds(ctx, None, "Ninja", "Status van de ninja's.")
    em.add_field(name="Aliassen", value=".ninja", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["mod", "moderator", "moderators"])
async def mods(ctx):
    em = embeds(ctx, None, "Moderator", "Status van de moderators.")
    em.add_field(name="Aliassen", value=".mod, .mods, .moderator, .moderators", inline=False)
    await ctx.send(embed=em)


@help.command(aliases=["latencie", "vertraging", "delay", "latency"])
async def ping(ctx):
    em = embeds(ctx, None, "Ping", "Weergeeft de bots ping (vertraging van de bot).")
    em.add_field(name="Aliassen", value=".ping, .latencie, .vertraging, .delay, .latency", inline=False)
    await ctx.send(embed=em)
    
@help.command(aliases=["members", "membercount", "member"])
async def member_count(ctx):
  em = embeds(ctx, None, "Membercount", "Weergeeft het aantal bots en members.")
  em.add_field(name="Aliassen", value=".member_count, .membercount, .members, .member", inline=False)
  await ctx.send(embed=em)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass


keep_alive()
client.run(os.getenv("token"))
