import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

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

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


roles_programmeren = {"gamedev":"[Game-Dev]", "python" : "[Python]", "3D":"[3D-Modeler]", "maker" :"[Maker]", "java":"[Java-Dev]", "cpp" :"[C]", "webdesign": "[WebDesigner]", "scratch":"[Scratch]"}
roles_lid_jaren = {"🧙\u200d♂️": "[>8 jaar lid]", "🧙": "[6-8 jaar lid]", "🧑\u200d⚖️":"[4-6 jaar lid]", "🧑\u200d🎓":"[2-4 jaar lid]", "🧑\u200d💻":"[1-2 jaar lid]", "🧒": "[<1 jaar lid]", "👤" : "[geen lid]"}
roles_leeftijd = {"🎱":"[> 18 jaar]", "🏀":"[17-18 jaar]", "🏈":"[15-16 jaar]", "⚽":"[13-14 jaar]"}
roles_computer = {"🖥️":"[expert]", "💻" : "[ervaren]", "📱" : "[gemiddeld]", "📠":"[beginner]"}
roles_os = {"linux":"[Linux User]","windows":"[Windows User]", "Apple":"[Apple User]"}


@client.event
async def on_raw_reaction_add(payload):
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
    if isinstance(error, commands.CommandNotFound):
        pass


keep_alive()
client.run(os.getenv('token'))
