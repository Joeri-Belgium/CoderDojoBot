import discord
from discord.ext import commands
import asyncio
import random
import os


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
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="to .help"))


@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id == 832221302769057822:
        guild = client.get_guild(payload.guild_id)
        msg = await client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
        await msg.remove_reaction(payload.emoji, payload.member)
        category_open = discord.utils.get(guild.categories, id=790237644482674688)
        global overwrites_create
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
                for n, tkmember in enumerate(ticket_members):
                    if n != 0:
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
        new_overwrites[member] = discord.PermissionOverwrite(view_channel=False, send_messages=False)
        await ctx.channel.edit(overwrites=new_overwrites)
        await ctx.send(embed=discord.Embed(color=member.color, title=None, description=f"{member.mention} is verwijdert uit {ctx.channel.mention}"))
        


@client.command(aliases=["hernoem"])
async def rename(ctx, *, channel_naam: str):
    channel_naam = channel_naam.lower()
    guild = ctx.guild
    category_open = discord.utils.get(guild.categories, id=790237644482674688)
    if ctx.channel in category_open.channels:
        if ("manage_channels", True) in ctx.author.permissions_in(ctx.channel):
            oude_naam = ctx.channel.name
            await ctx.channel.edit(name=str(channel_naam))
            await ctx.send(embed=discord.Embed(description=f"Kanaalnaam is verandert van {oude_naam} naar {channel_naam}"))
            
            
            
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
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        pass            

client.run("token")
