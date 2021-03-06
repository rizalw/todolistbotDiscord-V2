from discord.ext import commands
import discord 
import os

client = commands.Bot(command_prefix = "t!", help_command=None)

Token = "YOUR TOKEN"

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='My Maker Debug'))
    print("We have logged in as {}".format(client.user))

@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

if __name__ == "__main__":
    client.run(Token)
