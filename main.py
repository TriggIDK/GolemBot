import discord
from discord import Status, Activity, ActivityType
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
import os
import random
import requests
import json

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
bot = commands.Bot(command_prefix="slay", intents=intents, help_command=None)

# Stores ignored channels + welcome channels
ignored_channels = set()
welcome_channels = {}

CONFIG_FILE = "special_days.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"enabled": True, "channel_id": None, "days": {}}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

config = load_config()

# Daily task
@tasks.loop(hours=24)
async def daily_check():
    if not config.get("enabled"):
        return

    channel_id = config.get("channel_id")
    if channel_id is None:
        return

    channel = bot.get_channel(channel_id)
    if channel is None:
        return

    today = datetime.now().strftime("%m-%d")
    if today in config["days"]:
        message = config["days"][today]
        await channel.send(f"🎉 Today is: **{message}**")

@daily_check.before_loop
async def before_daily_check():
    await bot.wait_until_ready()
    # Sync to run at midnight
    now = datetime.now()
    target = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if now > target:
        target += timedelta(days=1)
    await discord.utils.sleep_until(target)

# Event: Bot ready
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

    await bot.change_presence(
        status=Status.dnd,
        activity=Activity(type=ActivityType.watching, name="Tiktoks of baddies | type slayhelp")
    )
    
    if not daily_check.is_running():
        daily_check.start()

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

# Custom Help Command
@bot.command(name="help")
async def custom_help(ctx):
    """Show this message."""
    embed = discord.Embed(
        title="LoraBot Help",
        description="Here are all the available commands:\n\n",
        color=discord.Color.gold()
    )

    for command in bot.commands:
        if not command.hidden:
            embed.add_field(
                name=f"slay{command.name}",
                value=command.help or "No description provided.",
                inline=False
            )

    embed.set_footer(text="Use slay<command> to run a command!")
    await ctx.send(embed=embed)

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
    """Say whatsup"""
    await ctx.send(f"Fakka niffo {ctx.author.mention}")

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
        await ctx.send(f"Sorry I am slow.")

@bot.command()
async def poll(ctx, *, question):
    """Start a poll"""
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
async def meghan(ctx):
    """Don't use this."""
    gif_url = "https://tenor.com/view/sneaky-golem-clash-royale-gif-18197200758540436087"
    await ctx.send(gif_url)

@bot.command()
async def dev(ctx):
    """Dev only command"""
    # Print to console for your own debugging
    print("TENOR API KEY LOADED:", bool(TENOR_API_KEY))
    print("DISCORD TOKEN LOADED:", bool(DISCORD_TOKEN))

@bot.command()
async def setdaychannel(ctx, channel: discord.TextChannel):
    """Set the channel where daily special day messages are sent."""
    config["channel_id"] = channel.id
    save_config(config)
    await ctx.send(f"Daily special day messages will be sent to {channel.mention}")

@bot.command()
async def addday(ctx, date: str, *, description: str):
    """Add a special day (format: MM-DD)"""
    try:
        datetime.strptime(date, "%m-%d")
    except ValueError:
        await ctx.send("Date format must be MM-DD (e.g., 09-08).")
        return

    config["days"][date] = description
    save_config(config)
    await ctx.send(f"Added special day: {date} → {description}")

@bot.command()
async def removeday(ctx, date: str):
    """Remove a special day"""
    if date in config["days"]:
        removed = config["days"].pop(date)
        save_config(config)
        await ctx.send(f"Removed {date} → {removed}")
    else:
        await ctx.send("Today is just a normal day bro.")

@bot.command()
async def days(ctx, toggle: str):
    """Enable or disable the daily notifications"""
    if toggle.lower() in ["on", "enable", "enabled"]:
        config["enabled"] = True
        save_config(config)
        await ctx.send("Daily notifications **enabled**")
    elif toggle.lower() in ["off", "disable", "disabled"]:
        config["enabled"] = False
        save_config(config)
        await ctx.send("Daily notifications **disabled**")
    else:
        await ctx.send("Please use `slaydays on` or `slaydays off`")

# Run bot
bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)
