import requests
from datetime import datetime
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
import DiscordUtils

# Load env file
load_dotenv()
api_url = os.getenv('API_URL')

# Instantiating the bot with a prefix
client = commands.Bot(command_prefix='rc', help_command=None, case_insensitive=True, strip_after_prefix=True, intents=discord.Intents.all()) 

# the on_ready function starts when the bot is ready to recieve commands 
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("with Faizan's ass"))
    print("Bot is ready")

#<--- Reccomendations --->

# Post recommendation to API
@client.command(aliases=['post rec', 'add'])
async def post_rec(ctx, rec_type:str):
    if rec_type in ('anime', 'manga', 'game', 'movie', 'web series', 'other'):
        if ctx.message.author.nick:
            author =  ctx.message.author.nick #Getting the command author's nickname in the server
        else:
            author = str(ctx.message.author).split('#')[0] # making do with the username if theres no nickname available
        
        await ctx.send("Enter the title of the recommendation below mate")
            
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        usr_input = await client.wait_for("message", check=check, timeout=60)

        post_req = requests.post(f'{api_url}/postrec/?rec_name={usr_input.content}&author={author}&rec_type={rec_type}')
        if post_req.status_code == 200: #checking if post request went alright
            await ctx.send('Your recommendation has been successfully added, trash taste btw')
        else:
            await ctx.send('Sorry, something went wrong check the error for more details') 
    else:
        await ctx.send('''Bruh specify the type of recommendation you want to add in the argument and make sure that its one of these:
(anime, manga, game, movie, web series, other)''')

#<-- Get reccomendations part -->

# Get recommendations list
def all_embeds(page:int, total_pages):
    response = requests.get(f'{api_url}/getrec/{page}').json()
    fetched_recs = response['rec_list']
    embed = discord.Embed(title="Akatsuki recommended", description="For when you can't find stuff to do", color=0xFF5733)
    for rec in fetched_recs:
        date_time = datetime.fromisoformat(rec[4])
        embed.add_field(name=rec[1], value=f'''```yaml
author: {rec[2]}  
type: {rec[3]}
date added: {date_time.date()} 
time added: {date_time.hour}:{date_time.minute}```
        ''')
    embed.set_footer(text=f'page: {page}/{total_pages}')
    return embed

# Send all available reccomendations
@client.command(aliases=['show recs', 'reclist'])
async def all_recs(ctx):
    await ctx.send('Fetching all available reccomendations, may take a while')

    total_pages = requests.get('{api_url}/total_rec_pages').json()

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, timeout=30)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⏪', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('⏩', "next")
    paginator.add_reaction('⏭️', "last")

    embeds = []
    for i in range(1, total_pages+1):
        embeds.append(all_embeds(i, total_pages))
    await paginator.run(embeds)

# Filter recs by author/rec_type
def filtered_embeds(choice:str, usr_input:str, page:int, total_pages):
    response = requests.get(f'{api_url}/recsfilter/{choice}/{usr_input}/{page}').json()
    fetched_recs = response['rec_list']
    embed = discord.Embed(title="Akatsuki recommended", description="For when you can't find stuff to do", color=0xFF5733)
    for rec in fetched_recs:
        date_time = datetime.fromisoformat(rec[4])
        embed.add_field(name=rec[1], value=f'''```yaml
author: {rec[2]}  
type: {rec[3]}
date added: {date_time.date()} 
time added: {date_time.hour}:{date_time.minute}```
        ''')
    embed.set_footer(text=f'page: {page}/{total_pages}')
    return embed

@client.command()
async def filter_recs(ctx, choice: str):
    # Usr can filter by rec_author or rec_type
    if choice == 'author' or choice == 'type':
        await ctx.send("Type in the name of the rec_author or rec_type you wanna filter the results by, bitch")
        
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        usr_input = await client.wait_for("message", check=check, timeout=60)

        # have to fetch atleast 1 page to get the total page size for the query
        filter_query = requests.get(f'{api_url}/recsfilter/{choice}/{usr_input.content}/1')
        if filter_query.status_code == 200:

            total_pages = filter_query.json()['total_pages']

            await ctx.send('Filtering recommendations be patient bro..')

            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
            embeds = []

            for i in range(1, total_pages+1):
                embeds.append(filtered_embeds(choice, usr_input.content, i, total_pages))
            await paginator.run(embeds)
        else:
            await ctx.send('Enter a valid author/rec_type you asshat 👺')
    else:
        await ctx.send('Bro the argument can be either **author** or **type** nothing else.')

# Global Errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("""There aint no command like that, you illiterate ass. 
Check the `aq help` command for a full list of commands.""")
    if isinstance(error, commands.BadArgument):
        await ctx.send("Check the arguments your trying to pass again, something's wrong with em")
    if isinstance(error, commands.TooManyArguments):
        await ctx.send("Your sending too many arguments man, slow down 🚦")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("""Missing required arguments detected, I need something to work with mate 😑
Check the `aq help` command for all required arguments of the commands available.""")

client.run(os.getenv('BOT_TOKEN'))