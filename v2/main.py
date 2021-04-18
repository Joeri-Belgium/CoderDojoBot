import discord
from discord.ext import commands
from keep_alive import keep_alive
import os

async def lijst_online_members(ctx, naam_role):
    lijst_role = [member for member in ctx.guild.members if naam_role in [role.name for role in member.roles]]
    lijst_online = [member.display_name for member in lijst_role if str(member.status) != "offline"]
    lijst_offline = [member.display_name for member in lijst_role if str(member.status) == "offline"]
    if not lijst_online:
        members_online = "/"
    else:
        members_online = ", ".join(lijst_online)
    if not lijst_offline:
        members_offline = "/"
    else:
        members_offline = ", ".join(lijst_offline)
    if not lijst_offline and not lijst_online:
        em = embeds(ctx, None, f"{naam_role}", "Niemand heeft deze role")
    else:
        em = embeds(ctx, None, f"{naam_role}", f"**Online ({len(lijst_online)}):** {members_online}\n**Offline ({len(lijst_offline)}):** {members_offline}")
    await ctx.send(embed=em)


def embeds(ctx, title, name, value):
    em = discord.Embed(color=ctx.author.color)
    em.add_field(name=name, value=value)
    return em


intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


@client.command(aliases=["latencie", "vertraging", "delay", "latency"])
async def ping(ctx):
    await ctx.send(embed=embeds(ctx, None, "Ping", f"The delay of the bot is: **{round(client.latency * 1000)}ms**."))

@client.command()
async def github(ctx):
    await ctx.send(embed=embeds(ctx, None, "Github", "De code van de CoderDojo Discord is terug te vinden op: https://github.com/beastmatser3/CoderDojoBot"))

@client.command()
async def bug(ctx):
    await ctx.send(embed=embeds(ctx, None, "Bug gevonden?", "Stuur een bericht naar beastmatser#0728 om de bug te reporten."))

@client.command(aliases=["py"])
async def python(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[Python]"))


@client.command(aliases=[])
async def scratch(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[Scratch]"))


@client.command(aliases=["web", "webdesign"])
async def webdesigner(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[WebDesigner]"))


@client.command(aliases=["javadev", "java-dev", "js"])
async def java(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[Java-Dev]"))


@client.command(aliases=["3D", "3d", "3D-Modelers", "3D-Modeler", "3D-modeler", "3D-modelers"])
async def d3(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[3D-Modeler]"))


@client.command(aliases=["makers"])
async def maker(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[Maker]"))


@client.command(aliases=["game-dev", "gamedev", "game"])
async def game_dev(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[Game-Dev]"))


@client.command(aliases=["c++", "c#"])
async def c(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[C]"))


@client.command(aliases=["modsontrail"])
async def modontrail(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[Moderator On Trial]"))


@client.command(aliases=["mods", "moderator", "moderators", "mod-"])
async def mod(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[Moderator]"))


@client.command(aliases=["coaches"])
async def coach(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[Coach]"))


@client.command(aliases=["ninjas"])
async def ninja(ctx):
    await ctx.send(embed=await lijst_online_members(ctx, "[Ninja]"))
    

@client.event
async def on_command_error(ctx, error):
    pass

keep_alive()
client.run(os.environ['token'])
