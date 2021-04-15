import discord
from discord.ext import commands
from keep_alive import keep_alive
import os

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


@client.command(aliases=["eenroles", "1role", "eenrole"])
@commands.has_permissions(administrator=True)
async def geen_roles(ctx):
    channel1 = client.get_channel(788696271720415242)
    channel2 = client.get_channel(818126902878404677)
    members = [member for member in ctx.guild.members if len(member.roles) == 2 and not member.bot]
    embed = discord.Embed(color=discord.Colour.lighter_grey())
    embed.add_field(name="Roles", value=f"We hebben opgemerkt dat je enkel de [Ninja]/[Coach] (die heb je waarschijnlijk van een moderator gekregen). In {channel2.mention} kan je door onder de berichten op de emoticons te klikken de overeenkomende roles krijgen. Dit staat ook in de tutorial van de server: https://www.youtube.com/watch?v=eMDVAxBPnhM&feature=youtu.be\n\nAls je er niet uit kan geraken kun je nog altijd een ticket (in {channel1.mention}) aanmaken.\n\n**Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.**")
    for member in members:
        await member.send(embed=embed)
    bericht_members = ', '.join([member.name for member in members])
    await ctx.send(embed=discord.Embed(color=ctx.author.color).add_field(name="Command succesvol opgeroepen", value=f"Volgende member(s) kregen een bericht: {bericht_members}"))

@client.command(aliases=["geefninja"])
@commands.has_permissions(administrator=True)
async def geef_ninja(ctx):
    role_ninja = discord.utils.get(ctx.guild.roles, name="[Ninja]")
    role_coach = discord.utils.get(ctx.guild.roles, name="[Coach]")
    not_bots = [member for member in ctx.guild.members if not member.bot]
    members = [member for member in not_bots if role_ninja not in member.roles and role_coach not in member.roles]
    for member in members:
        if not member.bot:
            embed = discord.Embed()
            embed.add_field(name=f"Hallo {member.name}!", value=f"We hebben gezien dat je nog geen roles hebt in de server, neem een kijkje in {client.get_channel(829633531579203595).mention} om daar jouw roles te krijgen, we hebben je alvast toegang gegeven tot de server \(:\n\n**Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.**")
            await member.add_roles(role_ninja)
            await member.send(embed=embed)
        else:
            pass
    bericht_members = ', '.join([member.name for member in members])
    embed = discord.Embed(color=ctx.author.color)
    if not members:
        embed.add_field(name="Command uitgevoerd, maar...", value="Iedereen heeft al een toepasselijke role (ninja, coach)")
    else:    
        embed.add_field(name="Command succesvol uitgevoerd", value=f"Volgende member(s) kregen de role [Ninja]: \n `{bericht_members}`")
    await ctx.send(embed=embed)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass


keep_alive()
client.run(os.environ['token'])
