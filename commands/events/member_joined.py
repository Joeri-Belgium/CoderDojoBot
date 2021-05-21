import discord
from discord.ext import commands

class Member_joined(commands.Cog):

    def __init__(self,client):
        self.client = client

    async def embeds(self, ctx, name, value):
        em = discord.Embed(color=ctx.author.color)
        em.add_field(name=name, value=value)
        await ctx.send(embed=em)

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


def setup(client):
    client.add_cog(Member_joined(client))