import discord
from discord.ext import commands
import asyncio
import random
import os

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

async def embeds(ctx, name, value):
    em = discord.Embed(color=ctx.author.color)
    em.add_field(name=name, value=value)
    await ctx.send(embed=em)


async def lijst_online_members(ctx, naam_role):
    lijst_role = [member for member in ctx.guild.members if naam_role in [role.name for role in member.roles]]
    lijst_online = [member.display_name.split(" [")[0] for member in lijst_role if str(member.status) != "offline"]
    lijst_offline = [member.display_name.split(" [")[0] for member in lijst_role if str(member.status) == "offline"]
    if not lijst_online:
        members_online = "/"
    else:
        members_online = ", ".join(lijst_online)
    if not lijst_offline:
        members_offline = "/"
    else:
        members_offline = ", ".join(lijst_offline)
    if not lijst_offline and not lijst_online:
        await embeds(ctx, f"{naam_role}", "Niemand heeft deze role")
    else:
        await embeds(ctx, f"{naam_role}", f"**Online ({len(lijst_online)}):** {members_online}\n**Offline ({len(lijst_offline)}):** {members_offline}")


async def max_n_role_toevoegen(payload, lijst_role, n):
        member_roles = [role.name for role in payload.member.roles]
        if len(set(member_roles).intersection(lijst_role.values())) >= n:
            msg = await client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, payload.member)
            embed = discord.Embed(color=discord.Colour.blurple())
            try:
                embed.add_field(name=f"Je mag maar {n} role(s) van deze soort hebben!", value=f"```Role die je wou: {lijst_role[payload.emoji.name]}```\n```Role(s) die je hebt: {', '.join(set(member_roles).intersection(lijst_role.values()))}```")
                await payload.member.send(embed=embed)
            except:
                pass
        else:
            for key in lijst_role:
                if key == payload.emoji.name:
                    role = discord.utils.get(payload.member.guild.roles, name=lijst_role[key])
                    await payload.member.add_roles(role)
                    
async def role_verwijderen(payload, lijst_role):
    for key in lijst_role:
            if key == payload.emoji.name:
                guild = client.get_guild(payload.guild_id)
                role = discord.utils.get(guild.roles, name=lijst_role[key])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)


roles_programmeren = {"gamedev":"[Game-Dev]", "python" : "[Python]", "3D":"[3D-Modeler]", "maker" :"[Maker]", "java":"[Java-Dev]", "cpp" :"[C]", "webdesign": "[WebDesigner]", "scratch":"[Scratch]"}
roles_lid_jaren = {"🧙\u200d♂️": "[>8 jaar lid]", "🧙": "[6-8 jaar lid]", "🧑\u200d⚖️":"[4-6 jaar lid]", "🧑\u200d🎓":"[2-4 jaar lid]", "🧑\u200d💻":"[1-2 jaar lid]", "🧒": "[<1 jaar lid]", "👤" : "[geen lid]"}
roles_leeftijd = {"🎱":"[> 18 jaar]", "🏀":"[17-18 jaar]", "🏈":"[15-16 jaar]", "⚽":"[13-14 jaar]"}
roles_computer = {"🖥️":"[expert]", "💻" : "[ervaren]", "📱" : "[gemiddeld]", "📠":"[beginner]"}
roles_os = {"linux":"[Linux User]","windows":"[Windows User]", "Apple":"[Apple User]"}       

intents = discord.Intents.all()
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")

@client.event
async def on_ready():
    print(f"{client.user.name} is up and running...")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".help"))


@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id == 832221302769057822:
        guild = client.get_guild(payload.guild_id)
        msg = await client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        category_open = discord.utils.get(guild.categories, id=790237644482674688)
        mod = discord.utils.get(guild.roles, name="[Moderator]")
        overwrites_create = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            mod : discord.PermissionOverwrite(view_channel=True),
            payload.member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await category_open.create_text_channel(f"{payload.member.display_name.split(' [')[0]}-ticket", overwrites=overwrites_create)
        await channel.send(content=payload.member.mention, embed=discord.Embed(color=payload.member.color, description="Hier kun je jouw probleem uitleggen. Geef zoveel mogelijk informatie en verwoord dit zo duidelijk mogelijk, op die manier kan je nog sneller geholpen worden.\nOm het ticket te sluiten, kan je het `.sluit` commando uitvoeren."))
    if payload.message_id == 830125441335427093:
        for key in roles_programmeren:
            if key == payload.emoji.name:
                role = discord.utils.get(payload.member.guild.roles, name=roles_programmeren[key])
                await payload.member.add_roles(role)
    elif payload.message_id == 830119299880452116:
        await max_n_role_toevoegen(payload, roles_lid_jaren, 1)
    elif payload.message_id == 830115776006324334:
        await max_n_role_toevoegen(payload, roles_leeftijd, 1)
    elif payload.message_id == 830121144614387763:
        await max_n_role_toevoegen(payload, roles_computer, 1)
    elif payload.message_id == 830123341474037790:
        await max_n_role_toevoegen(payload, roles_os, 2)
    elif payload.message_id == 830127528580612107:
        role = discord.utils.get(payload.member.guild.roles, name="[Ninja]")
        if payload.emoji.name != "ninja_":
            msg = await client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, payload.member)
        else:
            await payload.member.add_roles(role)

       

@client.command(aliases=["sluit"])
async def close(ctx):
    channel = ctx.channel
    guild = ctx.guild
    category_open = discord.utils.get(guild.categories, id=790237644482674688)
    if ctx.channel in category_open.channels:
        def check(payload):
            global emoji
            emoji = payload.emoji.name
            return payload.message_id == msg.id and payload.user_id != 808736566213345281
        def check1(payload):
            global emoji
            emoji = payload.emoji.name
            return payload.message_id == msg.id and payload.user_id != 808736566213345281 and (emoji == "⛔" or emoji == "🔓")

        mod = discord.utils.get(guild.roles, name="[Moderator]")
        members = [i for i in channel.overwrites if isinstance(i, discord.Member)]
        overwrites = {
            mod : discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.default_role: discord.PermissionOverwrite(view_channel=False)         
        }
        for member in members:           
            overwrites[member] = discord.PermissionOverwrite(view_channel=False)
        category_closed = discord.utils.get(guild.categories, id=790237755049115669)
        await channel.edit(category=category_closed , overwrites=overwrites)
        embed = discord.Embed(description="\⛔ : Verwijder dit ticket\n\🔓: Heropen dit ticket\n\📜: Maak een transcript (`.txt` bestand) van dit ticket")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("⛔")
        await msg.add_reaction("🔓")
        await msg.add_reaction("📜")
        await client.wait_for("raw_reaction_add", check=check)
        if emoji == "🔓":
            new_overwrites = msg.channel.overwrites
            ticket_members = [k for k in channel.overwrites if isinstance(k, discord.Member)]
            if len(ticket_members) >= 2:
                for tkmember in ticket_members:
                    if ("external_emojis", False) not in msg.author.permissions_in(msg.channel):
                        new_overwrites[tkmember] = discord.PermissionOverwrite(view_channel=True)
            await channel.edit(category=category_open, overwrites=new_overwrites)
            await ctx.message.delete()
            await msg.delete()
        elif emoji == "📜":
            with open(f"{channel.id}.txt", "w", encoding="utf+8") as f:
                async for i in channel.history(limit=None, oldest_first=True):
                    f.write(f"\n{i.author.name}: {i.content}")
            await channel.send(file=discord.File(f"{channel.id}.txt"))
            os.remove(f"{channel.id}.txt")
            await client.wait_for("raw_reaction_add", check=check1)
            if emoji == "⛔":
                await channel.send(embed=discord.Embed(color=discord.Colour.dark_blue(), description=f"{channel.mention} wordt verwijdert binnen 5 seconden!"))
                await asyncio.sleep(5)
                await channel.delete()
            elif emoji == "🔓":
                await channel.edit(category=category_open, overwrites=channel.overwrites)
                await ctx.message.delete()
                await msg.delete()
        elif emoji == "⛔":
            await channel.send(embed=discord.Embed(color=discord.Colour.dark_blue(), description=f"{channel.mention} wordt verwijderd binnen 5 seconden!"))
            await asyncio.sleep(5)
            await channel.delete()
            
@client.command()
async def add(ctx, member: discord.Member):
    guild = ctx.guild
    category_open = discord.utils.get(guild.categories, id=790237644482674688)
    if ctx.channel in category_open.channels:
        new_overwrites = ctx.channel.overwrites
        new_overwrites[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=False)
        await ctx.channel.edit(overwrites=new_overwrites)
        await ctx.send(embed=discord.Embed(color=member.color, title=None, description=f"{member.mention} is toegevoegd aan {ctx.channel.mention}"))
        
        
@client.command()
async def remove(ctx, member: discord.Member):
    guild = ctx.guild
    category_open = discord.utils.get(guild.categories, id=790237644482674688)
    if ctx.channel in category_open.channels:
        new_overwrites = ctx.channel.overwrites
        new_overwrites[member] = discord.PermissionOverwrite(view_channel=False, send_messages=False, external_emojis=False)
        await ctx.channel.edit(overwrites=new_overwrites)
        await ctx.send(embed=discord.Embed(color=member.color, description=f"{member.mention} is verwijderd uit {ctx.channel.mention}"))
        


@client.command(aliases=["hernoem"])
@commands.cooldown(1, 300, commands.BucketType.channel)
async def rename(ctx, *, channel_naam: str):
    channel_naam = str(channel_naam.lower()[:100])
    guild = ctx.guild
    category_open = discord.utils.get(guild.categories, id=790237644482674688)
    if ctx.channel in category_open.channels and ("manage_channels", True) in ctx.author.permissions_in(ctx.channel):
        oude_naam = ctx.channel.name
        await ctx.channel.edit(name=channel_naam)
        await ctx.send(embed=discord.Embed(description=f"Kanaalnaam is verandert van {oude_naam} naar {channel_naam}"))
            
@client.command()
@commands.has_permissions(administrator=True)
async def create(ctx, dojo):
  guild = ctx.guild
  perms = discord.Permissions(2251673153)
  role = await guild.create_role(name=f"[Dojo {dojo.title()}]", permissions=perms, mentionable=True)
  category = discord.utils.get(ctx.guild.categories, id=830431636616904745)
  overwrites = {
    guild.default_role: discord.PermissionOverwrite(read_messages=False),
    role : discord.PermissionOverwrite(read_messages=True)
  }
  await category.create_text_channel("💬" + dojo + " chat", overwrites=overwrites)
  await category.create_voice_channel("📢" + dojo + " voice", overwrites=overwrites)
  await ctx.send(embed=discord.Embed(description=f"{dojo.capitalize()} role, tekst- en voicekanaal werden aangemaakt!"))

@client.command(aliases=["dojo's"])
async def dojos(ctx):
  category = discord.utils.get(ctx.guild.categories, id=830431636616904745)
  dojos = [text_channel.name.split("💬")[1].split("-")[0].title() for text_channel in category.text_channels]
  embed = discord.Embed(color=ctx.author.color)
  embed.add_field(name="Dojo's met een privéchat:", value=f"```{', '.join(dojos)}```")
  embed.set_footer(text="Als je zelf zo'n een kanaal wilt als coach, maak dan een ticket aan.")
  await ctx.send(embed=embed)

@client.command()
async def dojo(ctx, role_naam):
  role_naam = role_naam.capitalize()
  roles_dojos = [role.name for role in ctx.guild.roles[1:] if role.name.startswith("[Dojo")]
  for role in roles_dojos:
    if role_naam in role:
      await role_controle(ctx, role)
      break
  
@client.command(aliases=["eenroles", "1role", "eenrole"])
@commands.has_permissions(administrator=True)
async def geen_roles(ctx):
    channel1 = client.get_channel(788696271720415242)
    channel2 = client.get_channel(788693992510193694)
    members = [member for member in ctx.guild.members if len(member.roles) == 2]
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

@client.command(aliases=["latencie", "vertraging", "delay", "latency"])
async def ping(ctx):
    await embeds(ctx, "Ping", f"The delay of the bot is: **{round(client.latency * 1000)}ms**.")

@client.command()
async def github(ctx):
    await embeds(ctx, "Github", "De code van de CoderDojo Discord is terug te vinden op: https://github.com/beastmatser3/CoderDojoBot")

@client.command()
async def bug(ctx):
    await embeds(ctx, "Bug gevonden?", "Stuur een bericht naar beastmatser#0728 om de bug te reporten.")

@client.command(aliases=["py"])
async def python(ctx):
    await lijst_online_members(ctx, "[Python]")


@client.command(aliases=[])
async def scratch(ctx):
    await lijst_online_members(ctx, "[Scratch]")


@client.command(aliases=["web", "webdesign"])
async def webdesigner(ctx):
    await lijst_online_members(ctx, "[WebDesigner]")


@client.command(aliases=["javadev", "java-dev", "js"])
async def java(ctx):
    await lijst_online_members(ctx, "[Java-Dev]")


@client.command(aliases=["3D", "3d", "3D-Modelers", "3D-Modeler", "3D-modeler", "3D-modelers"])
async def d3(ctx):
    await lijst_online_members(ctx, "[3D-Modeler]")


@client.command(aliases=["makers"])
async def maker(ctx):
    await lijst_online_members(ctx, "[Maker]")


@client.command(aliases=["game-dev", "gamedev", "game"])
async def game_dev(ctx):
    await lijst_online_members(ctx, "[Game-Dev]")


@client.command(aliases=["c++", "c#"])
async def c(ctx):
    await lijst_online_members(ctx, "[C]")


@client.command(aliases=["modsontrail"])
async def modontrail(ctx):
    await lijst_online_members(ctx, "[Moderator On Trial]")


@client.command(aliases=["mods", "moderator", "moderators", "mod-"])
async def mod(ctx):
    await lijst_online_members(ctx, "[Moderator]")


@client.command(aliases=["coaches"])
async def coach(ctx):
    await lijst_online_members(ctx, "[Coach]")


@client.command(aliases=["ninjas"])
async def ninja(ctx):
    await lijst_online_members(ctx, "[Ninja]")
    
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
  role_names = [role.name for role in ctx.author.roles]
  if "[Admin]" in role_names or "[Moderator]" in role_names:
    def check1(m):
      return m.channel == ctx.channel and m.author == ctx.author
    def check2(payload):
      if msg.id == payload.message_id and payload.user_id != 808736566213345281 and "[Moderator]" in role_names and payload.emoji.name == "🛑":
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
    embed.set_footer(text="Druk op '✅' om mee te doen met de sessie")
    msg = await client.get_channel(832263662566637640).send(embed=embed)
    await msg.add_reaction("✅")
    await msg.add_reaction("🛑")
    await client.wait_for("raw_reaction_add", check=check2)
    embed.set_footer(text="Deze sessie is afgelopen!")
    await msg.clear_reactions()
    await msg.edit(embed=embed)
  else:
    ticket_channel = client.get_channel(788696271720415242)
    embed = discord.Embed()
    embed.add_field(name="Helaas...", value=f"{ctx.author.name.split('[')[0]}, zonder de coach role kun je geen sessie maken! Als je toch iets wil doen kun je een ticket aanmaken ({ticket_channel.mention}).")
    await ctx.send(embed=embed)
            
@client.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == 830125441335427093:
            for key in roles_programmeren:
                if key == payload.emoji.name:
                    guild = client.get_guild(payload.guild_id)
                    role = discord.utils.get(guild.roles, name=roles_programmeren[key])
                    member = guild.get_member(payload.user_id)
                    await member.remove_roles(role)
    elif payload.message_id == 830119299880452116:
        await role_verwijderen(payload, roles_lid_jaren)
    elif payload.message_id == 830115776006324334:
        await role_verwijderen(payload, roles_leeftijd)
    elif payload.message_id == 830121144614387763:
        await role_verwijderen(payload, roles_computer)
    elif payload.message_id == 830123341474037790:
        await role_verwijderen(payload, roles_os)
    elif payload.message_id == 830127528580612107:
        if payload.emoji.name != "ninja_":
            pass
        else:
            guild = client.get_guild(payload.guild_id)
            role = discord.utils.get(guild.roles, name="[Ninja]")
            member = guild.get_member(payload.user_id)
            await member.remove_roles(role)
            
@client.event
async def on_voice_state_update(member, before, after):
    if after.channel:
        if after.channel.id == 788707011361505320:
            def check(member, before, after):
                return len(channel.members) == 0
            category = discord.utils.get(member.guild.categories, id=788707010451472405)
            ninja = discord.utils.get(member.guild.roles, id=790285278858182686)
            coach = discord.utils.get(member.guild.roles, id=790284978365661245)
            overwrites = {
                member : discord.PermissionOverwrite(manage_channels=True),
                member.guild.default_role : discord.PermissionOverwrite(view_channel=False),
                ninja : discord.PermissionOverwrite(view_channel=True),
                coach : discord.PermissionOverwrite(view_channel=True)
            }
            naam = member.display_name.split(" [")[0]
            if naam.endswith("s"):    
                channel = await category.create_voice_channel(name=f"{naam}' kanaal", overwrites=overwrites)
            elif naam.endswith(("a", "e", "i", "o", "u", "y")):
                channel = await category.create_voice_channel(name=f"{naam}'s kanaal", overwrites=overwrites)
            else: 
                channel = await category.create_voice_channel(name=f"{naam}s kanaal", overwrites=overwrites)
            await member.move_to(channel)
            await client.wait_for("voice_state_update", check=check)
            await channel.delete()

@client.event
async def on_member_join(member):
  introductie = client.get_channel(829633531579203595)
  regels = client.get_channel(790536868236099604)
  hoe_discord_gebruiken = client.get_channel(788694027359748106)
  maak_ticket_channel = client.get_channel(788696271720415242)
  embed = discord.Embed(title="**Welkom**", description=f"Welkom bij de **CoderDojo Discord** server, {member.name}! Dit is de plek waar je jouw vragen kunt stellen over code gerelateerde zaken!\n\nOm van start te gaan moet je even een korte **vragenlijst** invullen in {introductie.mention}, zo komen we een beetje meer te weten over jouw kennen en kunnen.\n\nDe **regels** van de server moeten ten alle tijden worden gevolgd, deze regels kan je terugvinden in {regels.mention}.\n\nWe zouden ook heel graag hebben dat iedereen herkenbaar is, daarom zouden we je willen vragen om je **nickname**  te veranderen naar je voornaam gevolgd door de stad van jouw dojo tussen vierkante haakjes. Dit ziet er dan bv. zo uit: `Bart [Antwerpen]`. Heb je geen dojo kan je `Bart [Geen dojo]` neerplaatsen.\n\nAls je niet weet hoe dit moet of je begrijpt niet helemaal hoe Discord werkt staat er in {hoe_discord_gebruiken.mention} een **tutorial** die je kan bekijken.\n\nHeb je hulp nodig in verband met de Discord server, wil je feedback geven, een suggestie doen of iets melden over een bepaalde persoon? Je kan altijd een **ticket** aanmaken in {maak_ticket_channel.mention} en dan zal je zo snel mogelijk hulp krijgen.")
  embed.set_footer(text="Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.")
  await member.send(embed=embed)
            
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandOnCooldown):
        seconden = error.retry_after % 60
        minuten = (error.retry_after - seconden) / 60
        if minuten == 0:
            await ctx.send(embed=discord.Embed(description=f"Wacht nog `{round(seconden, 1)}` om dit command te gebruiken in dit kanaal!"))
        else:
            await ctx.send(embed=discord.Embed(description=f"Wacht nog `{round(minuten)} min en {round(seconden, 1)}s` om dit command te gebruiken in dit kanaal!"))
    elif isinstance(error, commands.errors.CommandNotFound):
        pass            

client.run("ODA4NzM2NTY2MjEzMzQ1Mjgx.YCK4ng.yqnNXYBGjE_3oTTdwIAMEEMumkc")
