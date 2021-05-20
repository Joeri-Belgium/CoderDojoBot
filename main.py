import discord
from discord.ext import commands
import asyncio
import os
from discord.ext.commands.converter import MemberConverter
import requests
from bs4 import BeautifulSoup
from packages import packages
import random
import sqlite3
from PIL import Image, ImageDraw, ImageFont

intents = discord.Intents.all()
client = commands.Bot(command_prefix=".", intents=intents)
client.remove_command("help")


@client.event
async def on_ready():
    print(f"{client.user.name} is running...")
    discord.Activity(type=discord.ActivityType.watching, name=".help")

# Command loader
for root, subFolder, files in os.walk(f'./commands'):
    for item in files:
        if item.endswith('.py'):
            file_path = str(os.path.join(root,item))
            file_path = file_path.replace("\\", ".")
            client.load_extension(file_path[2:-3])
            print("loaded command: ",item)
        

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
            
            async def closing_functions(emoji):
                if emoji == "🔓":
                    
                    new_overwrites = msg.channel.overwrites
                    ticket_members = [k for k in channel.overwrites if isinstance(k, discord.Member)]
                    
                    for ticket_member in ticket_members:
                        new_overwrites[ticket_member] = discord.PermissionOverwrite(view_channel=True)
                    
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
                
                elif emoji == "⛔":
                    await channel.send(embed=discord.Embed(color=discord.Colour.dark_blue(), description=f"{channel.mention} wordt verwijderd binnen 5 seconden!"))
                    await asyncio.sleep(5)
                    await channel.delete()
                    
            async def functions_after_txt(emoji):
                if emoji == "⛔":
                    await channel.send(embed=discord.Embed(color=discord.Colour.dark_blue(), description=f"{channel.mention} wordt verwijdert binnen 5 seconden!"))
                    await asyncio.sleep(5)
                    await channel.delete()
                
                elif emoji == "🔓":
                    await channel.edit(category=category_open, overwrites=channel.overwrites)
                    await ctx.message.delete()
                    await msg.delete()
            
            def check_reaction_on_close_msg(payload):
                if payload.message_id == msg.id and payload.user_id != 808736566213345281:
                    self.client.loop.create_task(closing_functions(payload.emoji.name))
                    return True
            
            def check_reaction_delete_reopen(payload):
                if payload.message_id == msg.id and payload.user_id != 808736566213345281 and payload.emoji.name in ("🔓", "⛔"):
                    self.client.loop.create_task(functions_after_txt(payload.emoji.name))
                    return True

            mod = discord.utils.get(guild.roles, name="[Moderator]")
            members = [i for i in channel.overwrites if isinstance(i, discord.Member)]
            overwrites = {
                mod : discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.default_role: discord.PermissionOverwrite(view_channel=False)         
            }
            for member in members:
                if mod not in member.roles:
                    overwrites[member] = discord.PermissionOverwrite(view_channel=False)
            
            category_closed = discord.utils.get(guild.categories, id=790237755049115669)
            await channel.edit(category=category_closed , overwrites=overwrites)
            embed = discord.Embed(description="\⛔ : Verwijder dit ticket\n\🔓: Heropen dit ticket\n\📜: Maak een transcript (`.txt` bestand) van dit ticket")
            msg = await ctx.send(embed=embed)
            
            await msg.add_reaction("⛔")
            await msg.add_reaction("🔓")
            await msg.add_reaction("📜")
            
            await self.client.wait_for("raw_reaction_add", check=check_reaction_on_close_msg)
                
    @commands.command()
    async def add(self, ctx, member: discord.Member):
        guild = ctx.guild
        category_open = discord.utils.get(guild.categories, id=790237644482674688)
        if ctx.channel in category_open.channels:
            await ctx.channel.set_permissions(member, read_messages=True, send_messages=True, view_channel=True)
            await ctx.send(embed=discord.Embed(color=member.color, description=f"{member.mention} is toegevoegd aan {ctx.channel.mention}"))
            
            
    @commands.command()
    async def remove(self, ctx, member: discord.Member):
        guild = ctx.guild
        category_open = discord.utils.get(guild.categories, id=790237644482674688)
        if ctx.channel in category_open.channels:
            await ctx.channel.set_permissions(member, overwrite=None)
            await ctx.send(embed=discord.Embed(color=member.color, description=f"{member.mention} is verwijderd uit {ctx.channel.mention}"))
            


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
                    user = guild.get_member(payload.user_id)
                    await user.remove_roles(role)
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
        guild = self.client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if payload.message_id == 830125441335427093:
                for key in self.roles_programmeren:
                    if key == payload.emoji.name:
                        role = discord.utils.get(guild.roles, name=self.roles_programmeren[key])
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
            role = discord.utils.get(guild.roles, id=790285278858182686)
            await member.remove_roles(role)


class MainCommands(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        
    async def embeds(self, ctx, name, value):
        em = discord.Embed(color=ctx.author.color)
        em.add_field(name=name, value=value)
        await ctx.send(embed=em)
        


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
        # welkom  bericht naar user
        introductie = self.client.get_channel(829633531579203595)
        regels = self.client.get_channel(790536868236099604)
        hoe_discord_gebruiken = self.client.get_channel(788694027359748106)
        maak_ticket_channel = self.client.get_channel(788696271720415242)
        
        embed = discord.Embed(title="**Welkom**", description=f"Welkom bij de **CoderDojo Discord** server, {member.name}! Dit is de plek waar je jouw vragen kunt stellen over code gerelateerde zaken!\n\nOm van start te gaan moet je even een korte **vragenlijst** invullen in {introductie.mention}, zo komen we een beetje meer te weten over jouw kennen en kunnen.\n\nDe **regels** van de server moeten ten alle tijden worden gevolgd, deze regels kan je terugvinden in {regels.mention}.\n\nWe zouden ook heel graag hebben dat iedereen herkenbaar is, daarom zouden we je willen vragen om je **nickname**  te veranderen naar je voornaam gevolgd door de stad van jouw dojo tussen vierkante haakjes. Dit ziet er dan bv. zo uit: `Bart [Antwerpen]`. Heb je geen dojo kan je `Bart [Geen dojo]` neerplaatsen.\n\nAls je niet weet hoe dit moet of je begrijpt niet helemaal hoe Discord werkt staat er in {hoe_discord_gebruiken.mention} een **tutorial** die je kan bekijken.\n\nHeb je hulp nodig in verband met de Discord server, wil je feedback geven, een suggestie doen of iets melden over een bepaalde persoon? Je kan altijd een **ticket** aanmaken in {maak_ticket_channel.mention} en dan zal je zo snel mogelijk hulp krijgen.")
        embed.set_footer(text="Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.")
        await member.send(embed=embed)

        # welkom bericht in kanaal
        welkom_kanaal = self.client.get_channel(806505967390162944)
        welkom_image = Image.open("welkom.png")

        draw = ImageDraw.Draw(welkom_image)
        lettertype = ImageFont.truetype("VAG_rounded_Light.ttf", 73)

        draw.text((395, 15), f"{member.name}!", fill=(255, 255, 255), font=lettertype)

        welkom_image.save(f"{member.name}_welkom.png")

        await welkom_kanaal.send(file=discord.File(f"{member.name}_welkom.png"))

        os.remove(f"{member.name}_welkom.png")

class AndereCommands(commands.Cog):
    def __init__(self, bot):
        self.client = bot
    
    async def role_controle(self, ctx, user, role_naam):
        role = discord.utils.get(ctx.guild.roles, name=f"[Dojo {role_naam}]")
        if role in user.roles:
            embed = discord.Embed(color=user.color, description=f"{role_naam} rol is verwijderd.")
            await user.remove_roles(role)
        else:
            embed = discord.Embed(color=user.color, description=f"{role_naam} rol is toegevoegd.")
            await user.add_roles(role)
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
    async def dojo(self, ctx, role_naam, *,user: discord.Member = None):
        member = user or ctx.author
        role_naam = role_naam.capitalize()
        roles_dojos = [role.name for role in ctx.guild.roles[1:] if role.name.startswith("[Dojo")]
        if "[Coach]" in [role.name for role in ctx.author.roles] or "[Moderator]" in [role.name for role in ctx.author.roles]:
            for role in roles_dojos:
                if role_naam in role:
                    await self.role_controle(ctx, member, role_naam)
                    break
        else:
            for role in roles_dojos:
                if role_naam in role:
                    await self.role_controle(ctx, ctx.author, role_naam)
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
    
    @commands.command()
    @commands.has_role(788449231806791740) # moderator role
    async def sessie(self, ctx):
        async def reactie_verwijderen(payload):
            await msg.remove_reaction(payload.emoji, payload.member)
            
        def check1(m):
            return m.channel == ctx.channel and m.author == ctx.author
            
        await ctx.send("Wat is de naam van je sessie?")
        sessie_naam = await self.client.wait_for('message', check=check1, timeout=300)
        await ctx.send("Wanneer gaat de sessie door?")
        sessie_datum = await self.client.wait_for('message', check=check1, timeout=300)
        await ctx.send("Een kleine beschrijving van de sessie:")
        sessie_beschrijving = await self.client.wait_for('message', check=check1, timeout=1000)
        await ctx.send("Wie geeft deze sessie?")
        sessie_host = await self.client.wait_for('message', check=check1, timeout=100)
        sessie_host = await MemberConverter().convert(ctx, sessie_host.content)
        await ctx.send("Hoeveel mensen mogen er maximum komen?")
        sessie_max = await self.client.wait_for('message', check=check1, timeout=100)
        embed = discord.Embed(title=sessie_naam.content, color=discord.Colour.blurple())
        embed.add_field(name="Datum", value=f"`{sessie_datum.content}`")
        embed.add_field(name="Beschrijving:", value=f"```{sessie_beschrijving.content}```", inline=False)
        embed.set_footer(text="Druk op '✅' om mee te doen met de sessie")
        embed.set_author(name=f"Gastheer: {sessie_host.name}", icon_url=sessie_host.avatar_url)
        msg = await self.client.get_channel(832263662566637640).send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("🛑")
        perms = discord.Permissions(3264065)
        role = await ctx.guild.create_role(name=sessie_naam.content.lower(), permissions=perms, colour=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), hoist=False, mentionable=True)
        await sessie_host.add_roles(role)
        category = discord.utils.get(ctx.guild.categories, id=836860552805482557)
        overwrites = {
            role: discord.PermissionOverwrite(view_channel=True),
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        channel = await ctx.guild.create_text_channel(name=sessie_naam.content, overwrites=overwrites, category=category)
        await channel.send(f"De sessie is succesvol aangemaakt! {sessie_host.mention}")
        conn = sqlite3.connect("CoderDojoDatabase.db")
        c = conn.cursor()
        c.execute("INSERT INTO sessie VALUES (?, ?, ?, ?)", (msg.id, channel.id, role.id, int(sessie_max.content)))
        conn.commit()
        conn.close()
         
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == 832263662566637640 and payload.emoji.name == "🛑":
            mod = discord.utils.get(self.client.get_guild(payload.guild_id).roles, id=788449231806791740)
            if mod in payload.member.roles:
                msg = await self.client.get_channel(832263662566637640).fetch_message(payload.message_id)
                embed = [em for em in msg.embeds][0]
                embed.set_footer(text="Deze sessie is afgelopen!")
                await msg.edit(embed=embed)
                await msg.clear_reactions()
            else:
                msg = await self.client.get_channel(832263662566637640).fetch_message(payload.message_id)
                await msg.remove_reaction(payload.emoji, payload.member)
        elif payload.channel_id == 832263662566637640 and payload.emoji.name == "✅" and payload.member.id != 808736566213345281:
            msg = await self.client.get_channel(832263662566637640).fetch_message(payload.message_id)
            conn = sqlite3.connect("CoderDojoDatabase.db")
            c = conn.cursor()
            c.execute("SELECT * FROM sessie WHERE msg_id = (?)", (msg.id,))
            data = c.fetchone()
            print(f"Toevoegen: {data}")
            if data[3] < len(msg.reactions):
                await msg.remove_reaction(payload.emoji, payload.member)
                await payload.member.send("Deze sessie zit al vol, sorry!")
            else:
                for msg_id, channel_id, role_id, max_members in c.fetchall():
                    guild = self.client.get_guild(payload.guild_id)
                    role = discord.utils.get(guild.roles, id=role_id)
                    await payload.member.add_roles(role)
                    await self.client.get_channel(channel_id).send(f"Welkom bij de sessie {payload.member.mention}!")
                
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id == 832263662566637640 and payload.emoji.name == "✅" and payload.user_id != 808736566213345281: 
            msg = await self.client.get_channel(832263662566637640).fetch_message(payload.message_id)
            conn = sqlite3.connect("CoderDojoDatabase.db")
            c = conn.cursor()
            c.execute("SELECT * FROM sessie WHERE msg_id = (?)", (payload.message_id,))
            data = c.fetchall()
            print(f"Verwijderen: {data}")
            if data[0][3] < len(msg.reactions) + 1:
                pass
            else:
                for msg_id, channel_id, role_id, max_members in data:
                    guild = self.client.get_guild(payload.guild_id)
                    role = discord.utils.get(guild.roles, id=role_id)
                    member = await self.client.get_guild(payload.guild_id).fetch_member(payload.user_id)
                    await member.remove_roles(role)
            conn.close()
    

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def delete(self, ctx):
        category = discord.utils.get(ctx.guild.categories, id=836860552805482557)
        if ctx.channel.category == category:
            channel = ctx.channel
            conn = sqlite3.connect("CoderDojoDatabase.db")
            c = conn.cursor()
            c.execute("SELECT * FROM sessie WHERE channel_id = (?)", (channel.id,))
            data = c.fetchone()
            print(f"DELETEN: {data}")
            role = discord.utils.get(ctx.guild.roles, id=data[2])
            await ctx.send(embed=discord.Embed(description=f"{role.mention} en {channel.mention} worden verwijderd binnen 5 seconden!"))
            await asyncio.sleep(5)
            await role.delete()
            await channel.delete()
            c.execute("DELETE FROM sessie WHERE channel_id = (?)", (channel.id,))
            conn.commit()
            conn.close()

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



class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        
    async def embeds(self, ctx, name, value):
        em = discord.Embed(color=ctx.author.color)
        em.add_field(name=name, value=value)
        await ctx.send(embed=em)

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        em = discord.Embed(title="Commands", description="Typ .help <command> voor meer informatie over die command.", color=ctx.author.color)
        em.add_field(name="**`.ping`**", value="Geeft de bots ping weer (vertraging van de bot).", inline=False)
        em.add_field(name="**`.<role>`**", value="Status van de <role>-programmeurs. (werkt voor bepaalde roles, typ **.help role** voor een volledige lijst)", inline=False)
        em.add_field(name="**`.sessie`**", value=f"Maakt een sessie aan in {client.get_channel(832263662566637640).mention}, enkel voor moderators en admins.")
        em.add_field(name="**`.pypi`, `.nuget`,`.npm`**", value="Zoekt naar packages op de toebehorende websites en geeft wat informatie weer over de zoekopdracht.\n`.pypi`: python, `nuget`: C , `.npm`: javascript", inline=False)
        em.add_field(name="**`.docs`**", value="Zoekt naar documentaties op de readthedocs.org website (meestal python)", inline=False)
        em.add_field(name="**`.github`**", value="Github pagina van de source code van CoderDojo Discord bot.", inline=False)
        em.add_field(name="**`.dojos`**", value="Weergeeft een lijst van alle dojo's met een privéchat, je kan je bij zo een dojo aansluiten door `.dojo <naam_dojo>` te typen (bv. `.dojo Leuven`).")
        em.add_field(name="**`.inschrijven`**", value="Geeft een lijst van toekomstige dojo's met directe linken om je in te schrijven weer.", inline=False)
        em.add_field(name="**`.wakkerworden`**", value="Geeft een lijst van kanalen in slaapmodus weer, door het overeenkomende nummer te typen (die je te zien krijgt als je dit command oproept) open je het overeenkomende kanaal.")
        em.add_field(name="**`.bug`**", value="Wat moet je doen als je een bug vindt?", inline=False)
        em.add_field(name="**`.membercount`**", value="Geeft het aantal bots en members weer.", inline=False)
        await ctx.send(embed=em)


    @help.command()
    async def role(self, ctx):
        em = await self.embeds(ctx, "Role", "Weergeeft online en offline members van een bepaalde role")
        em.add_field(name="Mogelijke rollen", value="python (py), scratch, webdesigner (web), java-dev (java), 3D-Modelers (3D), maker, game-dev (game), c (++) (#), modontrail (mod-), moderator (mod), coach, ninja", inline=False)
        await ctx.send(embed=em)
        
    @help.command()
    async def bug(self, ctx):
        em = await self.embeds(ctx, "Bug", "Wat moet je doen als je een bug vindt?")
        await ctx.send(embed=em)
        
        
    @help.command()
    async def github(self, ctx):
        em = await self.embeds(ctx, "Github", "Github pagina van de source code van CoderDojo Discord bot.")
        await ctx.send(embed=em)


    @help.command(aliases=["latencie", "vertraging", "delay", "latency"])
    async def ping(self, ctx):
        em = await self.embeds(ctx, "Ping", "Weergeeft de bots ping (vertraging van de bot).")
        em.add_field(name="Aliassen", value=".ping, .latencie, .vertraging, .delay, .latency", inline=False)
        await ctx.send(embed=em)
        
    @help.command(aliases=["members", "membercount", "member"])
    async def member_count(self, ctx):
        em = await self.embeds(ctx, "Membercount", "Weergeeft het aantal bots en members.")
        em.add_field(name="Aliassen", value=".member_count, .membercount, .members, .member", inline=False)
        await ctx.send(embed=em)

    @commands.group(invoke_without_command=True)
    async def modhelp(self, ctx):
        embed = discord.Embed(color=ctx.author.color)
        embed.add_field(name="`.geef_ninja`", value="Geeft members zonder roles de [Ninja] role.", inline=False)
        embed.add_field(name="`.1role`", value="Stuurt members die 1 role hebben ([Ninja] of [Coach]) een bericht met een verwijzing naar reaction roles", inline=False)
        embed.add_field(name="`.create`", value="Maakt een voice- en tekstkanaal aan in de categorie dojo's en een toebehorende role", inline=False)
        embed.add_field(name="`.slaap`", value="Het kanaal waarin het commando wordt opgeroepen gaat in slaapmodus, het kanaal wordt verplaatst naar [SLAPENDE KANALEN], zodat er geen berichten meer kunnen verzonden worden.")
        await ctx.send(embed=embed)

    @modhelp.command()
    async def create(self, ctx):
        embed = await self.embeds(ctx, ".create <naam dojo>", "Maakt een voice- en tekstkanaal aan in de categorie dojo's en een toebehorende role")
        await ctx.send(embed=embed)


class WebScraping(commands.Cog):
    def __init__(self, bot):
        self.client = bot
    
    
    def web_scraping(self, url):
        r = requests.get(url)
        return BeautifulSoup(r.text, "lxml")

    def controle(self, mod):
        if mod in packages:
            return True
        else: 
            return False

    @commands.command()
    async def pypi(self, ctx, *, module):
        module = module.strip().lower()
        if self.controle(module):
            embed = discord.Embed(color=ctx.author.color)
            embed.add_field(name=f"{module.capitalize()} is een standaard python package", value=f"Documentatie:\n3.6: https://docs.python.org/3.6/library/{module}.html#module-{module}\n3.7: https://docs.python.org/3.7/library/{module}.html#module-{module}\n3.8: https://docs.python.org/3.8/library/{module}.html#module-{module}\n3.9: https://docs.python.org/3.9/library/{module}.html#module-{module}\n")
        else:
            soup_search = self.web_scraping(f"https://pypi.org/search/?q={module}")
            if soup_search.find("div", class_="callout-block"):
                embed = discord.Embed(color=ctx.author.color)
                embed.add_field(name=f"Geen resulaten voor: `{module}`", value="\u200b")
            else:
                embed = discord.Embed(title=f"Module {module}", color=ctx.author.color)
                module_link = "https://pypi.org" + soup_search.find("a", class_="package-snippet")["href"] # link van eerste module in zoekresulaten
                soup_module = self.web_scraping(module_link) # eerste module in zoekresultaten
                how_to_install = soup_module.find("span", id="pip-command").text # pip install 'module'
                backslash = "\n" # backslash (niet in f-string)
                project_links = [f"[`{link.text.replace(backslash, '').strip()}`]({link['href']})" for link in soup_module.find_all("a", class_="vertical-tabs__tab vertical-tabs__tab--with-icon vertical-tabs__tab--condensed")] # alle project links
                project_links = project_links[:int(len(project_links) / 2)] # alle items waren dubbel dus de helft verwijdert
                module_beschrijving = soup_module.find("p", class_="package-description__summary").text # beschrijving van de module ophalen
                if not project_links:
                    project_links.append("`Er zijn geen project links gevonden`")
                soup_history = self.web_scraping(module_link + "#history") # soup maken van history van modulepagina
                laatse_release = [i.text for i in soup_history.find_all("p", class_="release__version")][0].replace(" ", "").replace("\n", "").replace("pre-release", " (pre-release)")
                laatse_release_date = soup_history.find("time", datetime=True)["datetime"].split("T")[0].strip()
                license_ = [p.text.split("License: ")[1] for p in soup_module.find_all("p") if p.text.startswith("License:")]
                license_.append("/")
                author = [p.text.split("Author: ")[1] for p in soup_module.find_all("p") if p.text.startswith("Author: ")]
                author.append("/")         
                embed.add_field(name=f"{module.capitalize()} beschrijving:", value=f"```{module_beschrijving}```")
                embed.add_field(name="Hoe te installeren?", value=f"```{how_to_install}```", inline=False)
                embed.add_field(name="Laatste release:", value=f"```{laatse_release.strip()} ({laatse_release_date})```")
                embed.add_field(name="Licensie:", value=f"```{license_[0]}```")
                embed.add_field(name="Auteur:", value=f"```{author[0]}```")
                embed.add_field(name="Navigatie links", value=f"[`Beschrijving`]({module_link}#description)\n[`Geschiedenis`]({module_link}#history)\n[`Download files`]({module_link}#files)")
                embed.add_field(name=f"Project links", value="\n".join(project_links))
            embed.set_thumbnail(url="https://vichu006.gallerycdn.vsassets.io/extensions/vichu006/pypi-watcher/0.0.3/1591200523051/Microsoft.VisualStudio.Services.Icons.Default")
        await ctx.send(embed=embed)


    @commands.command()
    async def docs(self, ctx, *, module):
        module = module.strip().lower()
        if self.controle(module):
            embed = discord.Embed(color=ctx.author.color)
            embed.add_field(name=f"{module.capitalize()} is een standaard python package", value=f"Documentatie:\n3.6: https://docs.python.org/3.6/library/{module}.html#module-{module}\n3.7: https://docs.python.org/3.7/library/{module}.html#module-{module}\n3.8: https://docs.python.org/3.8/library/{module}.html#module-{module}\n3.9: https://docs.python.org/3.9/library/{module}.html#module-{module}\n")
        else:
            soup_results = self.web_scraping(f"https://readthedocs.org/search/?q={module}") # module opzoeken
            if not [i for i in soup_results.find_all("span", class_="quiet")]:
                result = soup_results.find("p", class_="module-item-title").find("a")["href"] # link van eerste module
                soup_doc = self.web_scraping(f"https://readthedocs.org{result}") # soup van eerste module
                if  len([i.text for i in soup_doc.find_all("pre", style="line-height: 1.25; white-space: pre;")]) != 1 and module != "matplotlib":
                    embed = discord.Embed(title=f"Module {module.capitalize()}", color=ctx.author.color)
                    git_rep = soup_doc.find("div", class_="project-view-docs").find("a")["href"]
                    link_doc = soup_doc.find("div", class_="project-view-docs").find("a")["href"]
                    embed.add_field(name=f"Documentatie {module}:", value=f"[```{link_doc}```]({link_doc})")
                    embed.add_field(name="Github repository:", value=f"[```{git_rep}```]({git_rep})")
                else:
                    embed = discord.Embed(color=ctx.author.color)
                    embed.add_field(name="Helaas...", value=f"{module.capitalize()} heeft geen readthedocs webpagina")
            else:
                embed = discord.Embed(color=ctx.author.color)
                embed.add_field(name=f"Geen resulaten voor {module}", value="\u200b")
            embed.set_thumbnail(url="https://read-the-docs-guidelines.readthedocs-hosted.com/_images/logo-light.png")
        await ctx.send(embed=embed)
        
        
    @commands.command()
    async def nuget(self, ctx, *, package):
        package = package.strip().lower()
        soup_search = self.web_scraping(f"https://www.nuget.org/packages?q={package}")
        result = soup_search.find("article", class_="package")
        if not result:
            embed = discord.Embed(color=ctx.author.color)
            embed.add_field(name=f"Geen resultaten voor `{package}`", value="\u200b")
        else:
            package_link = soup_search.find("a", class_="package-title")["href"]
            soup_module = self.web_scraping(f"https://www.nuget.org{package_link}")
            package_info = soup_module.find("aside", class_="col-sm-3 package-details-info")
            project_link = package_info.find("a", title="Visit the project site to learn more about this package")["href"]
            project_beschrijving = soup_module.find("p").text
            owners = []
            download_info = []
            hoe_downloaden = soup_module.find("pre", id="package-manager-text").text
            embed = discord.Embed(color=ctx.author.color)
            embed.add_field(name="Hoe te installeren (met package mananger)", value=f"```{hoe_downloaden}```")
            embed.add_field(name=f"{package.capitalize()} beschrijving:", value=f"```{project_beschrijving}```", inline=False)
            for i in package_info.find_all("li"):
                if False:
                    pass
                elif i.find(class_="ms-Icon ms-Icon--Globe"):
                    embed.add_field(name="Project website:", value=f"[```Project website```]({i.find('a')['href']})")
                elif i.find(class_="ms-Icon ms-Icon--Certificate"):
                    license_ = i.find(attrs={"aria-label":True}).text
                    embed.add_field(name="Licencie:", value=f"[```{license_}```]({i.find('a')['href']})")
                elif i.find(class_="ms-Icon ms-Icon--History"):
                    embed.add_field(name="Laatsts bijgewerkt:", value=f"```{i.find('span').text}```")
                elif i.find(class_="ms-Icon ms-Icon--Download"):
                    download_info.append("Totaal aantal downloads: " + i.text.strip().replace(' total downloads', '').replace(',', ' '))
                elif i.find(class_="ms-Icon ms-Icon--Giftbox"):
                    download_info.append("Downloads van de recenste versie: " + i.text.strip().replace('of current version', '').strip())
                elif i.find(class_="ms-Icon ms-Icon--Financial"):
                    download_info.append("Downloads gemiddeld per dag: " + i.text.strip().strip().replace('per day (avg)', '').strip())
                elif i.find_all(class_="owner-image"):
                    owners.append(i.text.strip())
            backslash = "\n"
            embed.add_field(name="Owners:", value=f"```{', '.join(owners)}```")
            embed.add_field(name="Download info:", value=f"```{backslash.join(download_info)}```", inline=False)
        embed.set_thumbnail(url="https://www.nuget.org/Content/gallery/img/logo-og-600x600.png")
        await ctx.send(embed=embed)
        

    @commands.command()
    async def npm(self, ctx, *, package):
        package = package.strip()
        soup_search = self.web_scraping(f"https://www.npmjs.com/search?q={package}")
        try:
            link_package = soup_search.find("a", target="_self")["href"]
            beschrijving_package = soup_search.find("p", class_="_8fbbd57d f5 black-60 mt1 mb0 pv1 no-underline lh-copy").text
            embed = discord.Embed(color=ctx.author.color)
            soup_package = self.web_scraping(f"https://www.npmjs.com/{link_package}")
            embed.add_field(name="Hoe te installeren?", value=f"```{soup_package.find(title='Copy Command to Clipboard').text.strip()}```", inline=False)
            embed.add_field(name=f"{package.capitalize()} beschrijving", value=f"```{beschrijving_package}```", inline=False)    
            package_links = [link.find("a")["href"] for link in soup_package.find_all("p", class_="_40aff104 fw6 mb3 mt2 truncate black-80 f5")]
            embed.add_field(name="Hoofdpagina", value=f"[```Hoofdpagina```]({package_links[0]})")
            embed.add_field(name="Github", value=f"[```Github```]({package_links[1]})")
            package_info = soup_package.find_all("div", class_="_702d723c dib w-50 bb b--black-10 pr2")
            for i in package_info:
                if i.text.startswith("Version"):
                    embed.add_field(name="Versie:", value=f"```{i.text.split('Version')[1]}```")
                elif i.text.startswith("License"):
                    embed.add_field(name="Licensie:", value=f"```{i.text.split('License')[1]}```")
                elif i.text.startswith("Unpacked Size"):
                    embed.add_field(name="Grootte uitgepakt bestand:", value=f"```{i.text.split('Unpacked Size')[1]}```")
                elif i.text.startswith("Total Files"):
                    embed.add_field(name="Aantal files:", value=f"```{i.text.split('Total Files')[1]}```")
        except:
            embed = discord.Embed(color=ctx.author.color)
            embed.add_field(name="Helaas...", value=f"Er waren geen zoekresulaten vorr `{package}`")
        finally:
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Npm-logo.svg/800px-Npm-logo.svg.png")
            await ctx.send(embed=embed)
        

    @commands.command()
    async def inschrijven(self, ctx, index=1):
        index -= 1
        soup_search = self.web_scraping("https://www.coderdojobelgium.be/nl/praktisch/inschrijven")
        scripts = soup_search.find_all("script", type="text/javascript")
        alle_komende_dojos = [i.split('"')[0] for n, i in enumerate(str(scripts[-1]).split('\\nsystem\\/ajax\\/*"},')[-1].split('title":"')) if n != 0]
        komende_dojos = alle_komende_dojos[index*6:index*6+5]
        komende_dojos_links = [i.split('"')[0] for i in (str(scripts[-1]).split('\\nsystem\\/ajax\\/*"},')[-1].split('url":"'))][index*6+1:index*6+6]
        embed = discord.Embed(color=ctx.author.color)
        embed.add_field(name="Index:", value=f"Typ .inschrijven [index] voor meer resultaten, bv. `.inschrijven 3`", inline=False)
        embed.add_field(name="Komende dojo's:", value="\n".join([f"[`{naam}`]({link})" for naam, link in zip(komende_dojos, komende_dojos_links)]))
        embed.set_footer(text=f"Komende dojo's - Pagina {index + 1} van {int((len(alle_komende_dojos) - (len(alle_komende_dojos) % 5)) / 5 - 1)}")
        await ctx.send(embed=embed)


class SleepingChannels(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        
        
    async def slapende_kanalen_bericht_aanpassen(self):
        category_afk = discord.utils.get(self.client.get_guild(788428553339011123).categories, id=835425695483166730)
        
        slapend_kanaal = client.get_channel(835795055176319016)
        slapende_kanalen_bericht = await slapend_kanaal.fetch_message(slapend_kanaal.last_message_id)
            
        channels_message = [f"{channel.mention}" for n, channel in enumerate(category_afk.channels)]
        embed = discord.Embed(title="Slapende kanalen:" ,description="\n".join(channels_message) + f"\n\nTyp in {self.client.get_channel(790215104825262111).mention} `.wakkerworden` om een kanaal \"wakker\" te maken.")
                
        await slapende_kanalen_bericht.edit(embed=embed)

    @commands.command(aliases=["wakkerworden"])
    async def wakkermaken(self, ctx):
        
        async def kanaal_wakker_maken(num):
            channel_to_move = category_afk.channels[num - 1]        
        
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

            await self.slapende_kanalen_bericht_aanpassen()

        
        def check_nummer(msg):
            try:
                nummer = int(msg.content)
                if msg.author == ctx.author and msg.channel == ctx.channel and int(msg.content) in nummers:
                    self.client.loop.create_task(kanaal_wakker_maken(nummer))
                    return True
            except:
                pass
        
        category_afk = discord.utils.get(ctx.guild.categories, id=835425695483166730)
        channels_message = [f"{n + 1}: {channel.mention}" for n, channel in enumerate(category_afk.channels)]
        nummers = list(range(1, len(channels_message) + 1))
        
        embed = discord.Embed(title="Slapende kanalen:", description="\n".join(channels_message), color=ctx.author.color)
        embed.set_footer(text="Typ het overeenkomende nummer om het kanaal wakker te maken.")
        
        await ctx.send(embed=embed)
        await self.client.wait_for("message", check=check_nummer, timeout=60)
            
    @commands.command(aliases=["slaap"])
    @commands.has_permissions(administrator=True)
    async def sleep(self, ctx):
        
        category_awake = discord.utils.get(ctx.guild.categories, id=788428553339011125)
        category_afk = discord.utils.get(ctx.guild.categories, id=835425695483166730)
        
        async def editing_channels(emoji):
            if emoji == "✅":
                
                ninja = discord.utils.get(ctx.guild.roles, id=790285278858182686)
                coach = discord.utils.get(ctx.guild.roles, id=790284978365661245)
                mod = discord.utils.get(ctx.guild.roles, id=788449231806791740)
                
                overwrites = {
                    ninja: discord.PermissionOverwrite(view_channel=False),
                    coach: discord.PermissionOverwrite(view_channel=False),
                    mod: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)
                }
                
                await ctx.channel.edit(category=category_afk, overwrites=overwrites)
                await ctx.message.delete()
                await message.delete()
                
                await self.slapende_kanalen_bericht_aanpassen()
                
            else:
                message_annulatie = await ctx.send(embed=discord.Embed(description=f"{ctx.channel.mention} wordt niet verplaatst (dit bericht wordt binnen 10 seconden verwijderd)"))
                
                await asyncio.sleep(10)
                await ctx.message.delete()
                await message.delete()
                await message_annulatie.delete()
        
        def check_sleep(payload):
            if payload.member == ctx.author and payload.emoji.name in ("❎", "✅"):
                self.client.loop.create_task(editing_channels(payload.emoji.name))
                return True
        
        if ctx.channel.category == category_awake:
            embed = discord.Embed(description=f"Wil je {ctx.channel.mention} doen slapen?")
            embed.set_footer(text="✅ = ja, ❎ = nee")
            message = await ctx.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❎")
            await self.client.wait_for("raw_reaction_add", check=check_sleep, timeout=60) 


# @client.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.errors.CommandOnCooldown):
#         seconden = error.retry_after % 60
#         minuten = (error.retry_after - seconden) / 60
#         if minuten == 0:
#              await ctx.send(embed=discord.Embed(description=f"Wacht nog `{round(seconden, 1)}` om dit command te gebruiken in dit kanaal!"))
#         else:
#              await ctx.send(embed=discord.Embed(description=f"Wacht nog `{round(minuten)} min en {round(seconden, 1)}s` om dit command te gebruiken in dit kanaal!"))
#     elif isinstance(error, commands.MissingRole):
#         await ctx.send(embed=discord.Embed(description=f"Je mist de {ctx.guild.get_role(error.missing_role).mention} role om dit command te gebruiken!"))
#     else:
#          pass


client.add_cog(TicketSystem(client))
client.add_cog(ReactionRoles(client))
client.add_cog(MainCommands(client))
client.add_cog(AndereCommands(client))
client.add_cog(Comms(client))
#client.add_cog(HelpCommand(client))
client.add_cog(SleepingChannels(client))
client.add_cog(WebScraping(client))

client.run("")
