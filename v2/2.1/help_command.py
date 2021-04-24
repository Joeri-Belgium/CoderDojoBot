import os
import discord
from discord.ext import commands
from keep_alive import keep_alive
import os


def embeds(ctx, name, value):
    em = discord.Embed(color=ctx.author.color)
    em.add_field(name=name, value=value)
    return em


intents = discord.Intents.all()
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


@client.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title="Commands", description="Typ .help <command> voor meer informatie over die command.", color=ctx.author.color)
    em.add_field(name="**`.ping`**", value="Weergeeft de bots ping (vertraging van de bot).", inline=False)
    em.add_field(name="**`.<role>`**", value="Status van de <role>-programmeurs. (werkt voor bepaalde roles, typ **.help role** voor een volledige lijst)", inline=False)
    em.add_field(name="**`.sessie`**", value=f"Maakt een sessie aan in {client.get_channel(832263662566637640).mention}, enkel voor moderators en admins.")
    em.add_field(name="**`.pypi`, `.nuget`,`.npm`**", value="Zoekt naar packages op de toebehorende websites en geeft wat informatie weer over de zoekopdracht.\n`.pypi`: python, `nuget`: C , `.npm`: javascript", inline=False)
    em.add_field(name="**`.docs`**", value="Zoekt naar documentaties op de readthedocs.org website (meestal python)", inline=False)
    em.add_field(name="**`.github`**", value="Github pagina van de source code van CoderDojo Discord bot.", inline=False)
    em.add_field(name="**`.dojos`**", value="Weergeeft een lijst van alle dojo's met een privéchat, je kan je bij zo een dojo aansluiten door `.dojo <naam_dojo>` te typen (bv. `.dojo Leuven`).")
    em.add_field(name="**`.inschrijven`**", value="Geeft een lijst van toekomstige dojo's met directe linken om je in te schrijven.", inline=False)
    em.add_field(name="**`.wakkerworden`**", value="Weergeeft een lijst van kanalen in slaapmodus, door het overeenkomende nummer te typen (die je te zien krijgt als je dit command oproept) open je het overeenkomende kanaal.")
    em.add_field(name="**`.bug`**", value="Wat moet je doen als je een bug vindt?", inline=False)
    em.add_field(name="**`.membercount`**", value="Weergeeft het aantal bots en members.", inline=False)
    await ctx.send(embed=em)


@help.command()
async def role(ctx):
    em = embeds(ctx, "Role", "Weergeeft online en offline members van een bepaalde role")
    em.add_field(name="Mogelijke rollen", value="python (py), scratch, webdesigner (web), java-dev (java), 3D-Modelers (3D), maker, game-dev (game), c (++) (#), modontrail (mod-), moderator (mod), coach, ninja", inline=False)
    await ctx.send(embed=em)
    
@help.command()
async def bug(ctx):
    em = embeds(ctx, "Bug", "Wat moet je doen als je een bug vindt?")
    await ctx.send(embed=em)
    
    
@help.command()
async def github(ctx):
    em = embeds(ctx, "Github", "Github pagina van de source code van CoderDojo Discord bot.")
    await ctx.send(embed=em)


@help.command(aliases=["latencie", "vertraging", "delay", "latency"])
async def ping(ctx):
    em = embeds(ctx, "Ping", "Weergeeft de bots ping (vertraging van de bot).")
    em.add_field(name="Aliassen", value=".ping, .latencie, .vertraging, .delay, .latency", inline=False)
    await ctx.send(embed=em)
    
@help.command(aliases=["members", "membercount", "member"])
async def member_count(ctx):
  em = embeds(ctx, "Membercount", "Weergeeft het aantal bots en members.")
  em.add_field(name="Aliassen", value=".member_count, .membercount, .members, .member", inline=False)
  await ctx.send(embed=em)

@client.group(invoke_without_command=True)
async def modhelp(ctx):
    embed = discord.Embed(color=ctx.author.color)
    embed.add_field(name="`.geef_ninja`", value="Geeft members zonder roles de [Ninja] role.", inline=False)
    embed.add_field(name="`.1role`", value="Stuurt members die 1 role hebben ([Ninja] of [Coach]) een bericht met een verwijzing naar reaction roles", inline=False)
    embed.add_field(name="`.create`", value="Maakt een voice- en tekstkanaal aan in de categorie dojo's en een toebehorende role", inline=False)
    embed.add_field(name="`.slaap`", value="Het kanaal waarin het commando wordt opgeroepen gaat in slaapmodus, het kanaal wordt verplaatst naar [SLAPENDE KANALEN], zodat er geen berichten meer kunnen verzonden worden.")
    await ctx.send(embed=embed)

@modhelp.command()
async def create(ctx):
    embed = embeds(ctx, ".create <naam dojo>", "Maakt een voice- en tekstkanaal aan in de categorie dojo's en een toebehorende role")
    await ctx.send(embed=embed)


keep_alive()
client.run(os.environ['token1'])
