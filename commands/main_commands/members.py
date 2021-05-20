import discord
from discord.ext import commands

class Members(commands.Cog):

    def __init__(self,client):
        self.client = client

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
                await self.embeds(ctx, f"{naam_role} ({len(lijst_offline) + len(lijst_online)})", f"**Online ({len(lijst_online)}):** {members_online}\n**Offline ({len(lijst_offline)}):** {members_offline}")

    @commands.command(aliases=["members2","leden","whoisonline"])
    async def members(self, ctx, role = None):
        if not role == None:
         await self.lijst_online_members(ctx, role)
        else:
            online_bots = len([str(member.status) for member in ctx.guild.members if member.bot and str(member.status) != 'offline'])
            offline_bots = len([str(member.status) for member in ctx.guild.members if member.bot and str(member.status) == 'offline'])
            verified_members = len([member.name for member in ctx.guild.members if "[Coach]" in [role.name for role in member.roles] or "[Ninja]" in [role.name for role in member.roles]])
            unverified_members = len(ctx.guild.members) - online_bots - offline_bots - verified_members
            embed = discord.Embed(color=ctx.author.color)
            embed.add_field(name=f"Members ({verified_members + unverified_members}):", value=f"```Geveerifeerd: {verified_members}```\n```Niet geveerifeerd: {unverified_members}```")
            embed.add_field(name=f"Bots ({online_bots + offline_bots}):", value=f"```Online bots: {online_bots}```\n```Offline bots: {offline_bots}```")
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Members(client))