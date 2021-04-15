import discord
from discord.ext import commands
from keep_alive import keep_alive
import os

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")

async def role_controle(ctx, role_naam):
  role = discord.utils.get(ctx.guild.roles, name=role_naam)
  embed = discord.Embed(color=ctx.author.color)
  if role in ctx.author.roles:
    embed.add_field(name="Role aangepast", value=f"{role_naam} role is verwijdert")
    await ctx.author.remove_roles(role)
    await ctx.send(embed=embed)
  else:
    embed.add_field(name="Role aangepast", value=f"{role_naam} role is toegevoegd")
    await ctx.author.add_roles(role)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(administrator=True)
async def create(ctx, dojo):
  guild = ctx.guild
  perms = discord.Permissions(2251673153)
  role = await guild.create_role(name=f"[Dojo {dojo.title()}]", permissions=perms, mentionable=True)
  category = [category for category in ctx.guild.categories if category.name == "Dojo's"][0]
  overwrites = {
    guild.default_role: discord.PermissionOverwrite(read_messages=False),
    role : discord.PermissionOverwrite(read_messages=True)
  }
  await category.create_text_channel("💬" + dojo + " chat", overwrites=overwrites)
  await category.create_voice_channel("📢" + dojo + " voice", overwrites=overwrites)
  embed = discord.Embed(color=ctx.author.color)
  embed.add_field(name=f"{dojo} role, textchannel en voice channel werden aangemaakt", value=f"```@client.command()\nasync def {dojo.lower()}(ctx):\n  await role_controle(ctx, \"{role}\")```")
  await ctx.send(embed=embed)

@client.command(aliases=["dojo", "dojo's"])
async def dojos(ctx):
  category = [category for category in ctx.guild.categories if category.id == 830433489601822740][0]
  dojos = [text_channel.name.split("💬")[1].split("-")[0].title() for text_channel in category.text_channels]
  embed = discord.Embed(color=ctx.author.color)
  embed.add_field(name="Dojo's met een privéchat:", value=f"```{', '.join(dojos)}```")
  embed.set_footer(text="Als je zelf zo'n een kanaal wilt als coach, maak dan een ticket aan.")
  await ctx.send(embed=embed)

@client.command()
async def leuven(ctx):
  await role_controle(ctx, "[Dojo Leuven]")
  
@client.command()
async def vilvoorde(ctx):
  await role_controle(ctx, "[Dojo Vilvoorde]")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        pass

keep_alive()
client.run(os.environ['token'])
