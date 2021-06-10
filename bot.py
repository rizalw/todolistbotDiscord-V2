from discord.ext import commands
import discord 
from mysql.connector import connect, Error
import time


client = commands.Bot(command_prefix = "t!", help_command=None)

Token = "YOUR TOKEN"

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='My Maker Debug'))
    print("We have logged in as {}".format(client.user))

@client.command()
async def help(ctx):
    context = """```List of Commands!
    1. t!ping                         
    = return ping
    2. t!all                          
    = return all of registered tasks
    3. t!add <nama> <tanggal> <waktu> 
    = If you want to input a task
    4. t!update <target tugas> <choice> <new data>
    = If you want to update a value, before that you must specifiy which tugas you want to edit, 
    which value do you want to change, and the new data that you want to insert
    5. t!delete <id>                
    = If you want to delete a task based from it's id
    6. t!clear <number> (default value = 100)               
    = If you want to delete messages regardless if you have the permission or not 
        (Use it wisely!!!)
    (Example: t!clear 3, it gonna clear 3 messages above this command)
    7. t!help                         
    = Show this messages```"""
    await ctx.send(context)

@client.command()
async def ping(ctx):
    await ctx.send(str(round(client.latency * 100)) + "ms")

@client.command()
async def all(ctx):
    try:
        with connect(
            host="localhost",
            user="root",
            database ="todolistbot",
        ) as connection:
            all_query = "SELECT * FROM task ORDER BY id ASC;"
            with connection.cursor() as cursor:
                cursor.execute(all_query)
                result = cursor.fetchall()
            print(len(result))
    except Error as e:
        await ctx.send("```Data masih kosong```")
        print(e)
    else:
        if len(result) == 0:
            await ctx.send("```Data masih kosong```")
        else:
            count = 1
            for content in result:
                await ctx.send("**" + "Task " + str(count) + "**\t(id=" + str(content[0]) + ")")
                await ctx.send("```Nama\t\t\t\t\t\t\t: {}\nTanggal Deadline\t\t\t\t: {}\nWaktu Deadline\t\t\t\t  : {}```".format(content[1], content[2], content[3]))
                count += 1

@client.command()
async def add(ctx, nama, tanggal, waktu):
    try:
        with connect(
            host="localhost",
            user="root",
            database ="todolistbot",
        ) as connection:
            add_task_query = """
        INSERT INTO task (nama, tanggal, waktu) VALUES 
        ("{}", "{}", "{}");""".format(nama, tanggal, waktu)
            with connection.cursor() as cursor:
                cursor.execute(add_task_query)
                connection.commit()
    except Error as e:
        print(e)
        await ctx.send("Input Gagal")
    else:
        msg = await ctx.send("Data telah dimasukkan")
        time.sleep(5)
        await msg.delete()

@client.command()
async def delete(ctx, id):
    try:
        with connect(
            host="localhost",
            user="root",
            database ="todolistbot",
        ) as connection:
            delete_task_query = "DELETE FROM task WHERE id = {};".format(id)
            with connection.cursor() as cursor:
                cursor.execute(delete_task_query)
                connection.commit()
    except Error as e:
        print(e)
        await ctx.send("Hapus Gagal")
    else:
        msg = await ctx.send("Data telah dihapus")
        time.sleep(5)
        await msg.delete()

@client.command(pass_context=True)
async def clear(ctx, amount=100):
    channel = ctx.message.channel
    messages = []
    async for message in channel.history(limit=amount + 1):
        messages.append(message)
    await channel.delete_messages(messages)
    msg = await ctx.send('Messaged deleted.')
    time.sleep(5)
    await msg.delete()

client.run(Token)