from discord.ext import commands, tasks
import discord 
from mysql.connector import connect, Error
from datetime import datetime, time, timedelta
import asyncio
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
    except Error as e:
        await ctx.send("```Data masih kosong```")
        print(e)
    else:
        if len(result) == 0:
            await ctx.send("```Data masih kosong```")
        else:
            count = 1
            await ctx.send("**LIST OF REMAINING TASKS**")
            for content in result:
                tanggalwaktu_deadline = content[2] + " " + content[3]
                tanggalwaktu_deadline = datetime.strptime(tanggalwaktu_deadline, '%d/%m/%Y %H:%M:%S')
                tanggalwaktu_sekarang = datetime.now()
                sisa = str(tanggalwaktu_deadline - tanggalwaktu_sekarang).split()
                sisa_hari = sisa[0] + " " + sisa[1]
                sisa_waktu = sisa[2][0:8]
                await ctx.send("**" + "Task " + str(count) + "**\t(id=" + str(content[0]) + ")")
                await ctx.send("```Nama\t\t\t\t\t\t\t: {}\nTanggal Deadline\t\t\t\t: {}\nWaktu Deadline\t\t\t\t  : {}\nSisa Waktu\t\t\t\t\t  : {}```"\
                    .format(content[1], content[2], content[3], (sisa_hari + " " + sisa_waktu)))
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
async def update(ctx, target, choice, newdata):
    try:
        with connect(
            host="localhost",
            user="root",
            database ="todolistbot",
        ) as connection:
            if choice == "nama":
                alter_query = "UPDATE task SET nama = '{}' where id = {};".format(newdata, target)
            elif choice == "tanggal":
                alter_query = "UPDATE task SET tanggal = '{}' where id = {};".format(newdata, target)
            elif choice == "waktu":
                alter_query = "UPDATE task SET waktu = '{}' where id = {};".format(newdata, target)
            with connection.cursor() as cursor:
                cursor.execute(alter_query)
                connection.commit()
            
    except Error as e:
        print(e)
        await ctx.send("Update Gagal")
    else:
        msg = await ctx.send("Data telah diupdate")
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

async def reminder():
    await client.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
    ctx = client.get_channel(828984053700362261) # Note: It's more efficient to do bot.get_guild(guild_id).get_channel(channel_id) as there's less looping involved, but just get_channel still works fine
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
            await ctx.send("**REMAINDER!!!**")
            for content in result:
                await ctx.send("**" + "Task " + str(count) + "**\t(id=" + str(content[0]) + ")")
                await ctx.send("```Nama\t\t\t\t\t\t\t: {}\nTanggal Deadline\t\t\t\t: {}\nWaktu Deadline\t\t\t\t  : {}```".format(content[1], content[2], content[3]))
                count += 1

async def background_task():
    now = datetime.now()
    if now.time() > time(7, 0, 0):  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
    while True:
        now = datetime.now() # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
        target_time = datetime.combine(now.date(), time(7, 0, 0))  # 6:00 PM today (In UTC)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
        await reminder()  # Call the helper function that sends the message
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start a new iteration

if __name__ == "__main__":
    client.loop.create_task(background_task())
    client.run(Token)