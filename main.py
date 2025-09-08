import discord
from discord import Status, Activity, ActivityType
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
import requests

# Load token
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TENOR_API_KEY = os.getenv('TENOR_API_KEY')

# Logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True
intents.bans = True
intents.reactions = True
intents.dm_reactions = True

# Bot setup
bot = commands.Bot(command_prefix="slay", intents=intents)

# Stores ignored channels + welcome channels
ignored_channels = set()
welcome_channels = {}

# Event: Bot ready
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

    await bot.change_presence(
        status=Status.dnd,
        activity=Activity(type=ActivityType.watching, name="Tiktoks of baddies | type slayhelp")
    )

# Event: Member join
@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.id in welcome_channels:
        channel = bot.get_channel(welcome_channels[guild.id])
        if channel:
            await channel.send(f"Welcome!! Please leave. {member.mention}")
    else:
        await member.send(f"Welcome!! Please leave. {member.name}")

# Event: Message filtering
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif message.channel.id in ignored_channels:
        return

    msg_content = message.content.lower()

    if "league of legends" in msg_content:
        await message.delete()
        await message.channel.send(f"{message.author.mention} Don't ever say that again.")

    if "ranked" in msg_content:
        await message.delete()
        await message.channel.send(f"{message.author.mention} What the hell is wrong with you.")

    if "akame ga kill" in msg_content:
        await message.channel.send("OMGGGG I LOVE AKAME")

    await bot.process_commands(message)

# Commands
@bot.command()
@commands.has_permissions(manage_guild=True)
async def setwelcome(ctx, channel: discord.TextChannel):
    """Set the channel for welcome messages."""
    welcome_channels[ctx.guild.id] = channel.id
    await ctx.send(f"Welcome messages will now be sent in {channel.mention}")

@bot.command()
async def ignore(ctx, channel: discord.TextChannel):
    """Tell the bot to ignore a channel."""
    ignored_channels.add(channel.id)
    await ctx.send(f"{channel.mention} is now ignored")

@bot.command()
async def unignore(ctx, channel: discord.TextChannel):
    """Tell the bot to stop ignoring a channel."""
    ignored_channels.discard(channel.id)
    await ctx.send(f"{channel.mention} is no longer ignored")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Fakka niffo {ctx.author.mention}")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"You said {msg}")

@bot.command()
async def brb(ctx):
    await ctx.reply("You shouldn't have done that.")

@bot.command()
async def gif(ctx, *, search: str = "kitten"):
    """Send a random GIF from Tenor based on user keyword (default = kitten)."""
    url = f"https://tenor.googleapis.com/v2/search?q={search}&key={TENOR_API_KEY}&client_key=discordbot&limit=20"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            gif = random.choice(data["results"])
            gif_url = gif["media_formats"]["gif"]["url"]
            await ctx.send(gif_url)
        else:
            await ctx.send(f"I am blind and couldn't find any gifs for: **{search}**.")
    else:
        await ctx.send(f"Sorry I am slow. HTTP {response.status_code}: {response.text}")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
async def meghan(ctx):
    gif_url = "https://tenor.com/view/sneaky-golem-clash-royale-gif-18197200758540436087"
    await ctx.send(gif_url)

# Print to console for your own debugging
    print("TENOR API KEY LOADED:", bool(TENOR_API_KEY))
    print("DISCORD API KEY LOADED:", bool(DISCORD_TOKEN))
# Run bot
bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)
