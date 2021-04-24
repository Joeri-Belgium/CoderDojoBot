import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
client = commands.Bot(command_prefix=".", intents=intents)
client.remove_command("help")

@client.event
async def on_ready():
    print(f"{client.user.name} is running...")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=".help"))


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.client = bot
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == 832221302769057822:
            guild = self.client.get_guild(payload.guild_id)
            msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, payload.member)
            category_open = discord.utils.get(guild.categories, id=790237644482674688)
            mod = discord.utils.get(guild.roles, id=788449231806791740)
            overwrites_create = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                mod : discord.PermissionOverwrite(view_channel=True),
                payload.member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await category_open.create_text_channel(f"{payload.member.display_name.split(' [')[0]}-ticket", overwrites=overwrites_create)
            await channel.send(content=payload.member.mention, embed=discord.Embed(color=payload.member.color, description="Hier kun je jouw probleem uitleggen. Geef zoveel mogelijk informatie en verwoord dit zo duidelijk mogelijk, op die manier kan je nog sneller geholpen worden.\nOm het ticket te sluiten, kan je het `.sluit` commando uitvoeren."))


    @commands.command(aliases=["sluit"])
    async def close(self, ctx):
        channel = ctx.channel
        guild = ctx.guild
        category_open = discord.utils.get(guild.categories, id=790237644482674688)
        if ctx.channel in category_open.channels:
            def check_reaction_on_close_msg(payload):
                if payload.message_id == msg.id and payload.user_id != 808736566213345281:
                    global emoji
                    emoji = payload.emoji.name
                return True
            def check_reaction_delete_reopen(payload):
                if payload.message_id == msg.id and payload.user_id != 808736566213345281 and payload.emoji.name in ("🔓", "⛔"):
                    global emoji
                    emoji = payload.emoji.name
                    return True

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
            await self.client.wait_for("raw_reaction_add", check=check_reaction_on_close_msg)
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
                await self.client.wait_for("raw_reaction_add", check=check_reaction_delete_reopen)
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
                
    @commands.command()
    async def add(self, ctx, member: discord.Member):
        guild = ctx.guild
        category_open = discord.utils.get(guild.categories, id=790237644482674688)
        if ctx.channel in category_open.channels:
            await ctx.channel.set_permissions(member, read_messages=True, send_messages=True, view_channel=True)
            await ctx.send(embed=discord.Embed(color=member.color, title=None, description=f"{member.mention} is toegevoegd aan {ctx.channel.mention}"))
            
            
    @commands.command()
    async def remove(self, ctx, member: discord.Member):
        guild = ctx.guild
        category_open = discord.utils.get(guild.categories, id=790237644482674688)
        if ctx.channel in category_open.channels:
            await ctx.channel.set_permissions(member, overwrite=None)
            await ctx.send(embed=discord.Embed(color=member.color, title=None, description=f"{member.mention} is verwijderd uit {ctx.channel.mention}"))
            


    @commands.command(aliases=["hernoem"])
    @commands.cooldown(1, 300, commands.BucketType.channel)
    async def rename(self, ctx, *, channel_naam: str):
        channel_naam = str(channel_naam.lower()[:100])
        guild = ctx.guild
        category_open = discord.utils.get(guild.categories, id=790237644482674688)
        if ctx.channel in category_open.channels and ("manage_channels", True) in ctx.author.permissions_in(ctx.channel):
            oude_naam = ctx.channel.name
            await ctx.channel.edit(name=channel_naam)
            await ctx.send(embed=discord.Embed(description=f"Kanaalnaam is verandert van {oude_naam} naar {channel_naam}"))

        
class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        
        roles_programmeren = {"gamedev":"[Game-Dev]", "python" : "[Python]", "3D":"[3D-Modeler]", "maker" :"[Maker]", "java":"[Java-Dev]", "cpp" :"[C]", "webdesign": "[WebDesigner]", "scratch":"[Scratch]"}
        self.roles_programmeren = roles_programmeren    
                   
        roles_lid_jaren = {"🧙\u200d♂️": "[>8 jaar lid]", "🧙": "[6-8 jaar lid]", "🧑\u200d⚖️":"[4-6 jaar lid]", "🧑\u200d🎓":"[2-4 jaar lid]", "🧑\u200d💻":"[1-2 jaar lid]", "🧒": "[<1 jaar lid]", "👤" : "[geen lid]"}
        self.roles_lid_jaren = roles_lid_jaren
    
        roles_leeftijd = {"🎱":"[> 18 jaar]", "🏀":"[17-18 jaar]", "🏈":"[15-16 jaar]", "⚽":"[13-14 jaar]"}
        self.roles_leeftijd = roles_leeftijd
    
        roles_computer = {"🖥️":"[expert]", "💻" : "[ervaren]", "📱" : "[gemiddeld]", "📠":"[beginner]"}
        self.roles_computer = roles_computer
    
        roles_os = {"linux":"[Linux User]","windows":"[Windows User]", "Apple":"[Apple User]"}   
        self.roles_os = roles_os 
            
            
    async def max_n_role_toevoegen(self, payload, lijst_role, n):
        member_roles = [role.name for role in payload.member.roles]
        if len(set(member_roles).intersection(lijst_role.values())) >= n:
            msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
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
                    break     
     
    async def role_verwijderen(self, payload, lijst_role):
        for key in lijst_role:
                if key == payload.emoji.name:
                    guild = self.client.get_guild(payload.guild_id)
                    role = discord.utils.get(guild.roles, name=lijst_role[key])
                    member = guild.get_member(payload.user_id)
                    await member.remove_roles(role)
                    break
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == 830125441335427093:
            for key in self.roles_programmeren:
                if key == payload.emoji.name:
                    role = discord.utils.get(payload.member.guild.roles, name=self.roles_programmeren[key])
                    await payload.member.add_roles(role)
        elif payload.message_id == 830119299880452116:
            await self.max_n_role_toevoegen(payload, self.roles_lid_jaren, 1)
        elif payload.message_id == 830115776006324334:
            await self.max_n_role_toevoegen(payload, self.roles_leeftijd, 1)
        elif payload.message_id == 830121144614387763:
            await self.max_n_role_toevoegen(payload, self.roles_computer, 1)
        elif payload.message_id == 830123341474037790:
            await self.max_n_role_toevoegen(payload, self.roles_os, 2)
        elif payload.message_id == 830127528580612107:
            role = discord.utils.get(payload.member.guild.roles, name="[Ninja]")
            await payload.member.add_roles(role)
            
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id == 830125441335427093:
                for key in self.roles_programmeren:
                    if key == payload.emoji.name:
                        guild = self.client.get_guild(payload.guild_id)
                        role = discord.utils.get(guild.roles, name=self.roles_programmeren[key])
                        member = guild.get_member(payload.user_id)
                        await member.remove_roles(role)
                        break
        elif payload.message_id == 830119299880452116:
            await self.role_verwijderen(payload, self.roles_lid_jaren)
        elif payload.message_id == 830115776006324334:
            await self.role_verwijderen(payload, self.roles_leeftijd)
        elif payload.message_id == 830121144614387763:
            await self.role_verwijderen(payload, self.roles_computer)
        elif payload.message_id == 830123341474037790:
            await self.role_verwijderen(payload, self.roles_os)
        elif payload.message_id == 830127528580612107:
            role = discord.utils.get(self.client.get_guild(payload.guild_id), id=790285278858182686)
            await member.remove_roles(role)


class MainCommands(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        
    async def embeds(self, ctx, name, value):
        em = discord.Embed(color=ctx.author.color)
        em.add_field(name=name, value=value)
        await ctx.send(embed=em)
        
    async def lijst_online_members(self, ctx, naam_role):
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
            await self.embeds(ctx, f"{naam_role}", "Niemand heeft deze role")
        else:
            await self.embeds(ctx, f"{naam_role}", f"**Online ({len(lijst_online)}):** {members_online}\n**Offline ({len(lijst_offline)}):** {members_offline}")


    @commands.command(aliases=["latencie", "vertraging", "delay", "latency"])
    async def ping(self, ctx):
        await self.embeds(ctx, "Ping", f"The delay of the bot is: **{round(self.client.latency * 1000)}ms**.")

    @commands.command()
    async def github(self, ctx):
        await self.embeds(ctx, "Github", "De code van de CoderDojo Discord is terug te vinden op: https://github.com/beastmatser3/CoderDojoBot")

    @commands.command()
    async def bug(self, ctx):
        await self.embeds(ctx, "Bug gevonden?", "Stuur een bericht naar beastmatser#0728 om de bug te reporten.")

    @commands.command(aliases=["py"])
    async def python(self, ctx):
        await self.lijst_online_members(ctx, "[Python]")


    @commands.command(aliases=[])
    async def scratch(self, ctx):
        await self.lijst_online_members(ctx, "[Scratch]")


    @commands.command(aliases=["web", "webdesign"])
    async def webdesigner(self, ctx):
        await self.lijst_online_members(ctx, "[WebDesigner]")


    @commands.command(aliases=["javadev", "java-dev", "js"])
    async def java(self, ctx):
        await self.lijst_online_members(ctx, "[Java-Dev]")


    @commands.command(aliases=["3D", "3d", "3D-Modelers", "3D-Modeler", "3D-modeler", "3D-modelers"])
    async def d3(self, ctx):
        await self.lijst_online_members(ctx, "[3D-Modeler]")


    @commands.command(aliases=["makers"])
    async def maker(self, ctx):
        await self.lijst_online_members(ctx, "[Maker]")


    @commands.command(aliases=["game-dev", "gamedev", "game"])
    async def game_dev(self, ctx):
        await self.lijst_online_members(ctx, "[Game-Dev]")


    @commands.command(aliases=["c++", "c#"])
    async def c(self, ctx):
        await self.lijst_online_members(ctx, "[C]")


    @commands.command(aliases=["modsontrail"])
    async def modontrail(self, ctx):
        await self.lijst_online_members(ctx, "[Moderator On Trial]")


    @commands.command(aliases=["mods", "moderator", "moderators", "mod-"])
    async def mod(self, ctx):
        await self.lijst_online_members(ctx, "[Moderator]")


    @commands.command(aliases=["coaches"])
    async def coach(self, ctx):
        await self.lijst_online_members(ctx, "[Coach]")


    @commands.command(aliases=["ninjas"])
    async def ninja(self, ctx):
        await self.lijst_online_members(ctx, "[Ninja]")
        
    @commands.command(aliases=["admins"])
    async def admin(self, ctx):
        await self.lijst_online_members(ctx, "[Admin]")
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        introductie = self.client.get_channel(829633531579203595)
        regels = self.client.get_channel(790536868236099604)
        hoe_discord_gebruiken = self.client.get_channel(788694027359748106)
        maak_ticket_channel = self.client.get_channel(788696271720415242)
        embed = discord.Embed(title="**Welkom**", description=f"Welkom bij de **CoderDojo Discord** server, {member.name}! Dit is de plek waar je jouw vragen kunt stellen over code gerelateerde zaken!\n\nOm van start te gaan moet je even een korte **vragenlijst** invullen in {introductie.mention}, zo komen we een beetje meer te weten over jouw kennen en kunnen.\n\nDe **regels** van de server moeten ten alle tijden worden gevolgd, deze regels kan je terugvinden in {regels.mention}.\n\nWe zouden ook heel graag hebben dat iedereen herkenbaar is, daarom zouden we je willen vragen om je **nickname**  te veranderen naar je voornaam gevolgd door de stad van jouw dojo tussen vierkante haakjes. Dit ziet er dan bv. zo uit: `Bart [Antwerpen]`. Heb je geen dojo kan je `Bart [Geen dojo]` neerplaatsen.\n\nAls je niet weet hoe dit moet of je begrijpt niet helemaal hoe Discord werkt staat er in {hoe_discord_gebruiken.mention} een **tutorial** die je kan bekijken.\n\nHeb je hulp nodig in verband met de Discord server, wil je feedback geven, een suggestie doen of iets melden over een bepaalde persoon? Je kan altijd een **ticket** aanmaken in {maak_ticket_channel.mention} en dan zal je zo snel mogelijk hulp krijgen.")
        embed.set_footer(text="Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.")
        await member.send(embed=embed)



class AndereCommands(commands.Cog):
    def __init__(self, bot):
        self.client = bot
    
    async def role_controle(self, ctx, role_naam):
        role = discord.utils.get(ctx.guild.roles, name=role_naam)
        if role in ctx.author.roles:
            embed = discord.Embed(color=ctx.author.color, description=f"{role_naam} rol is verwijderd.")
            await ctx.author.remove_roles(role)
        else:
            embed = discord.Embed(color=ctx.author.color, description=f"{role_naam} rol is toegevoegd.")
            await ctx.author.add_roles(role)
        await ctx.send(embed=embed)
    
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create(self, ctx, dojo):
        guild = ctx.guild
        perms = discord.Permissions(2251673153)
        role = await guild.create_role(name=f"[Dojo {dojo.title()}]", permissions=perms, mentionable=True)
        category = discord.utils.get(ctx.guild.categories, id=830433489601822740)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            role : discord.PermissionOverwrite(read_messages=True)
        }
        await category.create_text_channel("💬" + dojo + " chat", overwrites=overwrites)
        await category.create_voice_channel("📢" + dojo + " voice", overwrites=overwrites)
        await ctx.send(embed=discord.Embed(description=f"{dojo.capitalize()} role, tekst- en voicekanaal werden aangemaakt!"))

    @commands.command(aliases=["dojo's"])
    async def dojos(self, ctx):
        category = discord.utils.get(ctx.guild.categories, id=830433489601822740)
        dojos = [text_channel.name.split("💬")[1].split("-")[0].title() for text_channel in category.text_channels]
        embed = discord.Embed(color=ctx.author.color)
        embed.add_field(name="Dojo's met een privéchat:", value=f"```{', '.join(dojos)}```")
        embed.set_footer(text="Als je zelf zo'n een kanaal wilt als coach, maak dan een ticket aan.")
        await ctx.send(embed=embed)

    @commands.command()
    async def dojo(self, ctx, role_naam):
        role_naam = role_naam.capitalize()
        roles_dojos = [role.name for role in ctx.guild.roles[1:] if role.name.startswith("[Dojo")]
        for role in roles_dojos:
            if role_naam in role:
                await self.role_controle(ctx, role)
                break
    
    @commands.command(aliases=["eenroles", "1role"])
    @commands.has_permissions(administrator=True)
    async def eenrole(self, ctx):
            channel_introductie = self.client.get_channel(829633531579203595)
            channel_ticket = self.client.get_channel(788696271720415242)
            channel_hoe_discord_gebruiken = self.client.get_channel(788694027359748106)
            members = [member for member in ctx.guild.members if len(member.roles) == 2 and not member.bot]
            embed = discord.Embed(color=discord.Colour.lighter_grey())
            embed.add_field(name="Rollen", value=f"We hebben opgemerkt dat je enkel over de [Ninja] of [Coach] rol beschikt, en die heb je waarschijnlijk van een moderator gekregen. In {channel_introductie.mention} kan je door de juiste rollen te kiezen (via de emoticons) een soort van profiel aanmaken. Zo weten andere gebruikers meer van jouw kennen en kunnen. Dit staat ook in de tutorial die je gemakkelijk even snel kan bekijken (de tutorial vind je terug in {channel_hoe_discord_gebruiken.mention}).\n\n Als je er niet uit geraakt kan je altijd een ticket aanmaken (in {channel_ticket.mention}) en dan zal je daar zo snel mogelijk hulp krijgen van een moderator.")
            embed.set_footer(text="Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.")
            for member in members:
                await member.send(embed=embed)
            bericht_members = ', '.join([member.name for member in members])
            await ctx.send(embed=discord.Embed(color=ctx.author.color).add_field(name="Command succesvol opgeroepen", value=f"Volgende member(s) kregen een bericht: {bericht_members}"))

    @commands.command(aliases=["geefninja"])
    @commands.has_permissions(administrator=True)
    async def geef_ninja(self, ctx):
        role_ninja = discord.utils.get(ctx.guild.roles, name="[Ninja]")
        role_coach = discord.utils.get(ctx.guild.roles, name="[Coach]")
        members = [member for member in ctx.guild.members if role_ninja not in member.roles and role_coach not in member.roles and not member.bot]
        for member in members:
            if not member.bot:
                embed = discord.Embed()
                embed.add_field(name=f"Hallo {member.name}!", value=f"We hebben gezien dat je nog geen roles hebt in de server, neem een kijkje in {self.client.get_channel(829633531579203595).mention} om daar jouw roles te krijgen, we hebben je alvast toegang gegeven tot de server \(:\n\n**Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.**")
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
        
        
    @commands.command(aliases=["membercount", "members", "member"])
    async def member_count(self, ctx):
        online_bots = len([str(member.status) for member in ctx.guild.members if member.bot and str(member.status) != 'offline'])
        offline_bots = len([str(member.status) for member in ctx.guild.members if member.bot and str(member.status) == 'offline'])
        verified_members = len([member.name for member in ctx.guild.members if "[Coach]" in [role.name for role in member.roles] or "[Ninja]" in [role.name for role in member.roles]])
        unverified_members = len(ctx.guild.members) - online_bots - offline_bots - verified_members
        embed = discord.Embed(color=ctx.author.color)
        embed.add_field(name="Members:", value=f"```Geveerifeerd: {verified_members}```\n```Niet geveerifeerd: {unverified_members}```")
        embed.add_field(name="Bots:", value=f"```Online bots: {online_bots}```\n```Offline bots: {offline_bots}```")
        await ctx.send(embed=embed)
    
    @commands.command()
    async def sessie(self, ctx):
        role_names = [role.name for role in ctx.author.roles]
        if "[Admin]" in role_names or "[Moderator]" in role_names:
            def check1(m):
                return m.channel == ctx.channel and m.author == ctx.author
            def check2(payload):
                if msg.id == payload.message_id and payload.user_id != 808736566213345281 and "[Moderator]" in role_names and payload.emoji.name == "🛑":
                    return True
            await ctx.send("Wat is de naam van je sessie?")
            sessie_naam = await self.client.wait_for('message', check=check1, timeout=180)
            await ctx.send("Wanneer gaat de sessie door?")
            sessie_datum = await self.client.wait_for('message', check=check1, timeout=180)
            await ctx.send("Een kleine beschrijving van de sessie:")
            sessie_beschrijving = await self.client.wait_for('message', check=check1, timeout=600)
            embed = discord.Embed(title=sessie_naam.content, color=discord.Colour.blurple())
            embed.add_field(name="Datum", value=f"`{sessie_datum.content}`")
            embed.add_field(name="Beschrijving:", value=f"```{sessie_beschrijving.content}```", inline=False)
            embed.set_footer(text="Druk op '✅' om mee te doen met de sessie")
            msg = await self.client.get_channel(832263662566637640).send(embed=embed)
            await msg.add_reaction("✅")
            await msg.add_reaction("🛑")
            await self.client.wait_for("raw_reaction_add", check=check2)
            embed.set_footer(text="Deze sessie is afgelopen!")
            await msg.clear_reactions()
            await msg.edit(embed=embed)
        else:
            ticket_channel = self.client.get_channel(788696271720415242)
            embed = discord.Embed()
            embed.add_field(name="Helaas...", value=f"{ctx.author.name.split('[')[0]}, zonder de coach role kun je geen sessie maken! Als je toch iets wil doen kun je een ticket aanmaken ({ticket_channel.mention}).")
            await ctx.send(embed=embed)    


class Comms(commands.Cog):
    def __init__(self, bot):
        self.client = bot        
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
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
                await self.client.wait_for("voice_state_update", check=check)
                await channel.delete()

    
    
class SleepingChannels(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command(aliases=["wakkerworden"])
    async def wakkermaken(self, ctx):
        def check_nummer(msg):
            global nummer
            try:
                nummer = int(msg.content)
            except:
                pass
            return msg.author == ctx.author and msg.channel == ctx.channel and int(msg.content) in nummers
        
        category_afk = discord.utils.get(ctx.guild.categories, id=835425695483166730)
        channels_message = [f"{n + 1}: {channel.mention}" for n, channel in enumerate(category_afk.channels)]
        nummers = list(range(1, len(channels_message) + 1))
        
        embed = discord.Embed(title="Slapende kanalen:", description="\n".join(channels_message), color=ctx.author.color)
        embed.set_footer(text="Typ het overeenkomende nummer om het kanaal wakker te maken.")
        
        await ctx.send(embed=embed)
        await self.client.wait_for("message", check=check_nummer, timeout=60)
        
        channel_to_move = category_afk.channels[nummer - 1]        
        
        ninja = discord.utils.get(ctx.guild.roles, id=790285278858182686)
        coach = discord.utils.get(ctx.guild.roles, id=790284978365661245)
        
        overwrites = {
            ninja: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            coach: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        new_category = discord.utils.get(ctx.guild.categories, id=788428553339011125)
        await channel_to_move.edit(overwrites=overwrites, category=new_category, position=self.client.get_channel(790215104825262111).position)
        
        await ctx.send(embed=discord.Embed(description=f"{channel_to_move.mention} is wakker geworden 🥱."))
        last_message = await channel_to_move.fetch_message(channel_to_move.last_message_id)
        await last_message.delete()



    @commands.command(aliases=["slaap"])
    @commands.has_permissions(administrator=True)
    async def sleep(self, ctx):
        def check_sleep(payload):
            global emoji
            emoji = payload.emoji.name
            return payload.member == ctx.author and payload.emoji.name in ("❎", "✅")
        
        category_awake = discord.utils.get(ctx.guild.categories, id=788428553339011125)
        category_afk = discord.utils.get(ctx.guild.categories, id=835425695483166730)
        
        if ctx.channel.category == category_awake:
            embed = discord.Embed(description=f"Wil je {ctx.channel.mention} doen slapen?")
            embed.set_footer(text="✅ = ja, ❎ = nee")
            message = await ctx.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❎")
            await self.client.wait_for("raw_reaction_add", check=check_sleep, timeout=60)
            if emoji == "✅":
                
                ninja = discord.utils.get(ctx.guild.roles, id=790285278858182686)
                coach = discord.utils.get(ctx.guild.roles, id=790284978365661245)
                
                overwrites = {
                    ninja: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                    coach: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)
                }
                await ctx.channel.edit(category=category_afk, overwrites=overwrites)
                await ctx.message.delete()
                await message.delete()
                await ctx.send(embed=discord.Embed(description=f"{ctx.channel.mention} is gesloten wegens inactiviteit, als je dit kanaal wil open typ in {self.client.get_channel(790215104825262111).mention} **`.wakkerworden`**, dan krijg je een lijst te zien van kanalen die ook aan het \"slapen\" zijn, typ het overeenkomende nummer en dit kanaal zal weer heropened worden!"))
            else:
                message_annulatie = await ctx.send(embed=discord.Embed(description=f"{ctx.channel.mention} wordt niet verplaatst (dit bericht wordt binnen 10 seconden verwijderd)"))
                await asyncio.sleep(10)
                await ctx.message.delete()
                await message.delete()
                await message_annulatie.delete()
                 
 
# @client.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.errors.CommandOnCooldown):
#         seconden = error.retry_after % 60
#         minuten = (error.retry_after - seconden) / 60
#         if minuten == 0:
#             await ctx.send(embed=discord.Embed(description=f"Wacht nog `{round(seconden, 1)}` om dit command te gebruiken in dit kanaal!"))
#         else:
#             await ctx.send(embed=discord.Embed(description=f"Wacht nog `{round(minuten)} min en {round(seconden, 1)}s` om dit command te gebruiken in dit kanaal!"))
#     else:
#         pass


client.add_cog(TicketSystem(client))
client.add_cog(ReactionRoles(client))
client.add_cog(MainCommands(client))
client.add_cog(AndereCommands(client))
client.add_cog(Comms(client))
client.add_cog(SleepingChannels(client))

client.run("ODA4NzM2NTY2MjEzMzQ1Mjgx.YCK4ng.qcIwhuqd79utj49RPk4MxVL8Uyc")
