import discord
from discord import Status, Activity, ActivityType
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

# Load token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

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
#stores the ignored channels
ignored_channels = set()

# Event: Bot ready
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

    await bot.change_presence(
        status=Status.dnd,
        activity=Activity(type=ActivityType.watching, name="Men | type slayhelp")
    )

# Event: Member joins
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome!! Please leave. {member.name}")

# Event: Message filtering
@bot.event
async def on_message(message):
    if message.author == bot.user:
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

    # Always process commands at the end
    await bot.process_commands(message)

# Commands
@bot.command()
async def ignore(ctx, channel: discord.TextChannel):
    """Tell the bot to ignore an irrelevant channel."""
    ignored_channels.add(channel.id)
    await ctx.send(f"{channel.mention} is now irrelevant")

@bot.command()
async def unignore(ctx, channel: discord.TextChannel):
    """Tell the bot to no longer ignore a relevant channel."""
    ignored_channels.discard(channel.id)
    await ctx.send(f" {channel.mention} is now irrelevant")

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
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
async def sneaky(ctx):
    gif_url = "https://tenor.com/view/sneaky-golem-clash-royale-gif-18197200758540436087"
    await ctx.send(gif_url)

# Run bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
