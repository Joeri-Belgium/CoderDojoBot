import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from packages import packages
import os 
from keep_alive import keep_alive
import lxml

intents = discord.Intents(
    messages=True, guilds=True, reactions=True, members=True, presences=True, bans=True
)
client = commands.Bot(command_prefix=".", intents=intents, help=None)
client.remove_command("help")


def web_scraping(url):
    r = requests.get(url)
    return BeautifulSoup(r.text, "lxml")

def controle(mod):
    if mod in packages:
        return True
    else: 
        return False

@client.command()
async def pypi(ctx, *, module):
    module = module.strip().lower()
    if controle(module):
        embed = discord.Embed(color=ctx.author.color)
        embed.add_field(name=f"{module.capitalize()} is een standaard python package", value=f"Documentatie:\n3.6: https://docs.python.org/3.6/library/{module}.html#module-{module}\n3.7: https://docs.python.org/3.7/library/{module}.html#module-{module}\n3.8: https://docs.python.org/3.8/library/{module}.html#module-{module}\n3.9: https://docs.python.org/3.9/library/{module}.html#module-{module}\n")
    else:
        soup_search = web_scraping(f"https://pypi.org/search/?q={module}")
        if soup_search.find("div", class_="callout-block"):
            embed = discord.Embed(color=ctx.author.color)
            embed.add_field(name=f"Geen resulaten voor: `{module}`", value="\u200b")
        else:
            embed = discord.Embed(title=f"Module {module}", color=ctx.author.color)
            module_link = "https://pypi.org" + soup_search.find("a", class_="package-snippet")["href"] # link van eerste module in zoekresulaten
            soup_module = web_scraping(module_link) # eerste module in zoekresultaten
            how_to_install = soup_module.find("span", id="pip-command").text # pip install 'module'
            backslash = "\n" # backslash (niet in f-string)
            project_links = [f"[`{link.text.replace(backslash, '').strip()}`]({link['href']})" for link in soup_module.find_all("a", class_="vertical-tabs__tab vertical-tabs__tab--with-icon vertical-tabs__tab--condensed")] # alle project links
            project_links = project_links[:int(len(project_links) / 2)] # alle items waren dubbel dus de helft verwijdert
            module_beschrijving = soup_module.find("p", class_="package-description__summary").text # beschrijving van de module ophalen
            if not project_links:
                project_links.append("`Er zijn geen project links gevonden`")
            soup_history = web_scraping(module_link + "#history") # soup maken van history van modulepagina
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


@client.command()
async def docs(ctx, *, module):
    module = module.strip().lower()
    if controle(module):
        embed = discord.Embed(color=ctx.author.color)
        embed.add_field(name=f"{module.capitalize()} is een standaard python package", value=f"Documentatie:\n3.6: https://docs.python.org/3.6/library/{module}.html#module-{module}\n3.7: https://docs.python.org/3.7/library/{module}.html#module-{module}\n3.8: https://docs.python.org/3.8/library/{module}.html#module-{module}\n3.9: https://docs.python.org/3.9/library/{module}.html#module-{module}\n")
    else:
        soup_results = web_scraping(f"https://readthedocs.org/search/?q={module}") # module opzoeken
        if not [i for i in soup_results.find_all("span", class_="quiet")]:
            result = soup_results.find("p", class_="module-item-title").find("a")["href"] # link van eerste module
            soup_doc = web_scraping(f"https://readthedocs.org{result}") # soup van eerste module
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
    
    
@client.command()
async def nuget(ctx, *, package):
    package = package.strip().lower()
    soup_search = web_scraping(f"https://www.nuget.org/packages?q={package}")
    result = soup_search.find("article", class_="package")
    if not result:
        embed = discord.Embed(color=ctx.author.color)
        embed.add_field(name=f"Geen resultaten voor `{package}`", value="\u200b")
    else:
        package_link = soup_search.find("a", class_="package-title")["href"]
        soup_module = web_scraping(f"https://www.nuget.org{package_link}")
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
    

@client.command()
async def npm(ctx, *, package):
    package = package.strip()
    soup_search = web_scraping(f"https://www.npmjs.com/search?q={package}")
    try:
        link_package = soup_search.find("a", target="_self")["href"]
        beschrijving_package = soup_search.find("p", class_="_8fbbd57d f5 black-60 mt1 mb0 pv1 no-underline lh-copy").text
        embed = discord.Embed(color=ctx.author.color)
        soup_package = web_scraping(f"https://www.npmjs.com/{link_package}")
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
    

@client.command()
async def inschrijven(ctx, index=1):
    index -= 1
    soup_search = web_scraping("https://www.coderdojobelgium.be/nl/praktisch/inschrijven")
    scripts = soup_search.find_all("script", type="text/javascript")
    alle_komende_dojos = [i.split('"')[0] for n, i in enumerate(str(scripts[-1]).split('\\nsystem\\/ajax\\/*"},')[-1].split('title":"')) if n != 0]
    komende_dojos = alle_komende_dojos[index*6:index*6+5]
    komende_dojos_links = [i.split('"')[0] for i in (str(scripts[-1]).split('\\nsystem\\/ajax\\/*"},')[-1].split('url":"'))][index*6+1:index*6+6]
    embed = discord.Embed(color=ctx.author.color)
    embed.add_field(name="Index:", value=f"Typ .inschrijven [index] voor meer resultaten", inline=False)
    embed.add_field(name="Komende dojo's:", value="\n".join([f"[`{naam}`]({link})" for naam, link in zip(komende_dojos, komende_dojos_links)]))
    embed.set_footer(text=f"Komende dojo's - Pagina {index + 1} van {int((len(alle_komende_dojos) - (len(alle_komende_dojos) % 5)) / 5 - 1)}")
    await ctx.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        pass



keep_alive()
client.run(os.environ['token'])
