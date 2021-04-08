import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

def lijst_online_members(ctx, naam_role):
    lijst_online = []
    lijst_offline = []
    for member in ctx.guild.members:
        for role in member.roles:
            if role.name == naam_role:
                if str(member.status) != "offline":
                    lijst_online.append(member.display_name)
                else:
                    lijst_offline.append(member.display_name)
    if len(lijst_online) == 0:
        members_online = "/"
    else:
        members_online = ", ".join(lijst_online)
    if len(lijst_offline) == 0:
        members_offline = "/"
    else:
        members_offline = ", ".join(lijst_offline)
    if len(lijst_online) == 0 and len(lijst_offline) == 0:
        em = embeds(ctx, None, f"{naam_role}", "Niemand heeft deze role")
    else:
        em = embeds(ctx, None, f"{naam_role}", f"**Online ({len(lijst_online)}):** {members_online}\n**Offline ({len(lijst_offline)}):** {members_offline}")
    return em


def embeds(ctx, title, name, value):
    em = discord.Embed(title=title, color=ctx.author.color)
    em.add_field(name=name, value=value)
    return em


intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")

@client.command(aliases=["geenroles", "geenrole", "geen-role", "geen_roles", "geef_ninja", "geefninja", "membercount", "members", "member_count"])
async def help(ctx):
  pass


@client.command(aliases=["latencie", "vertraging", "delay", "latency"])
async def ping(ctx):
    await ctx.send(embed=embeds(ctx, None, "Ping", f"The delay of the bot is: **{round(client.latency * 1000)}ms**."))


@client.command(aliases=["py"])
async def python(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[Python]"))


@client.command(aliases=[])
async def scratch(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[Scratch]"))


@client.command(aliases=["web", "webdesign"])
async def webdesigner(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[WebDesigner]"))


@client.command(aliases=["javadev", "java-dev", "js"])
async def java(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[Java-Dev]"))


@client.command(aliases=["3D", "3d", "3D-Modelers", "3D-Modeler", "3D-modeler", "3D-modelers"])
async def d3(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[3D-Modeler]"))


@client.command(aliases=["makers"])
async def maker(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[Maker]"))


@client.command(aliases=["game-dev", "gamedev", "game"])
async def game_dev(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[Game-Dev]"))


@client.command(aliases=[])
async def c(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[C]"))


@client.command(aliases=["modsontrail"])
async def modontrail(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[Moderator On Trial]"))


@client.command(aliases=["mods", "moderator", "moderators"])
async def mod(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[Moderator]"))


@client.command(aliases=["coaches"])
async def coach(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[Coach]"))


@client.command(aliases=["ninjas"])
async def ninja(ctx):
    await ctx.send(embed=lijst_online_members(ctx, "[Ninja]"))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=embeds(ctx, None, "*E*```R```***R***O*~~R~~", "Helaas, dit is geen command!"))



keep_alive()
client.run(os.getenv("token"))
