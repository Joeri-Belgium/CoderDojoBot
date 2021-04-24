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
  introductie = client.get_channel(829633531579203595)
  regels = client.get_channel(790536868236099604)
  hoe_discord_gebruiken = client.get_channel(788694027359748106)
  maak_ticket_channel = client.get_channel(788696271720415242)
  embed = discord.Embed(title="**Welkom**", description=f"Welkom bij de **CoderDojo Discord** server, {member.name}! Dit is de plek waar je jouw vragen kunt stellen over code gerelateerde zaken!\n\nOm van start te gaan moet je even een korte **vragenlijst** invullen in {introductie.mention}, zo komen we een beetje meer te weten over jouw kennen en kunnen.\n\nDe **regels** van de server moeten ten alle tijden worden gevolgd, deze regels kan je terugvinden in {regels.mention}.\n\nWe zouden ook heel graag hebben dat iedereen herkenbaar is, daarom zouden we je willen vragen om je **nickname**  te veranderen naar je voornaam gevolgd door de stad van jouw dojo tussen vierkante haakjes. Dit ziet er dan bv. zo uit: `Bart [Antwerpen]`. Heb je geen dojo kan je `Bart [Geen dojo]` neerplaatsen.\n\nAls je niet weet hoe dit moet of je begrijpt niet helemaal hoe Discord werkt staat er in {hoe_discord_gebruiken.mention} een **tutorial** die je kan bekijken.\n\nHeb je hulp nodig in verband met de Discord server, wil je feedback geven, een suggestie doen of iets melden over een bepaalde persoon? Je kan altijd een **ticket** aanmaken in {maak_ticket_channel.mention} en dan zal je zo snel mogelijk hulp krijgen.")
  embed.set_footer(text="Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.")
  await member.send(embed=embed)

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
  coach = discord.utils.get(ctx.guild.roles, name="[Coach]")
  if coach in ctx.author.roles:
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
  else:
    ticket_channel = client.get_channel(788696271720415242)
    embed = discord.Embed()
    embed.add_field(name="Helaas...", value=f"{ctx.author.name.split('[')[0]}, zonder de coach role kun je geen sessie maken! Als je toch iets wil doen kun je een ticket aanmaken ({ticket_channel.mention}).")
    await ctx.send(embed=embed)


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
