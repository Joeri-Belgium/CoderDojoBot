import discord
from discord.ext import commands
import asyncio
import os
from keep_alive import keep_alive

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")

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
        embed = discord.Embed(title=None, description="\⛔ : Verwijder dit ticket\n\🔓: Heropen dit ticket\n\📜: Maak een transcript (`.txt` bestand) van dit ticket")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("⛔")
        await msg.add_reaction("🔓")
        await msg.add_reaction("📜")
        await client.wait_for("raw_reaction_add", check=check)
        if emoji == "🔓":
            new_overwrites = overwrites_create.copy()
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
                await channel.edit(category=category_open, overwrites=overwrites_create)
                await ctx.message.delete()
                await msg.delete()
        elif emoji == "⛔":
            await channel.send(embed=discord.Embed(color=discord.Colour.dark_blue(), description=f"{channel.mention} wordt verwijdert binnen 5 seconden!"))
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
        
        
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        pass

keep_alive()
client.run(os.environ['token'])
