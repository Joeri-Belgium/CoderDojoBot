import discord
from discord.ext import commands
import os
from keep_alive import keep_alive


intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


@client.command(aliases=["geenroles", "geenrole", "geen-role"])
@commands.has_permissions(ban_members=True)
async def geen_roles(ctx):
    counter = 0
    for member in ctx.guild.members:
        if len(member.roles) == 2:
            counter += 1
            em = discord.Embed(title=None)
            em.add_field(
                name="Roles",
                value=
                "We hebben opgemerkt dat je enkel de [Ninja]/[Coach] (die heb je waarschijnlijk van een moderator gekregen). In #introductie kan je door onder de berichten op de emoticons te klikken de overeenkomende roles krijgen. Dit staat ook in de tutorial van de server: https://www.youtube.com/watch?v=eMDVAxBPnhM&feature=youtu.be\n\nAls je er niet uit kan geraken kun je nog altijd een ticket (in #maak-ticket) aanmaken.\n\n**Dit is een geautomatiseerd bericht, antwoorden worden niet gelezen.**"
            )
            await member.send(embed=em)
    if counter == 1:
        await ctx.send(f"{counter} member kreeg een bericht.")
    else:
        await ctx.send(f"{counter} members kregen een bericht.")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass


keep_alive()
client.run(os.getenv("token"))
