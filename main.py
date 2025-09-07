import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True
intents.polls = True
intents.bans = True
intents.reactions = True
intents.dm_reactions = True

bot = commands.Bot(command_prefix="slay", intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go in {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"The the golem has been waiting for you {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "league of legends" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} Don't ever say that again.")
    
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Fakka niffo {ctx.author.mention}")

# change dm so that it sends a golem image to dm
@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")

# change to a funny thing that starts after a minute
@bot.command()
async def pekka(ctx):
    await ctx.reply("You shouldn't have done that.")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()    
async def sneaky(ctx):
    gif_url = "https://tenor.com/view/sneaky-golem-clash-royale-gif-18197200758540436087"
    await ctx.send(gif_url)

@bot.command()
async def akame(ctx):
    await ctx.reply("OMGGGG I LOVE AKAME")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)