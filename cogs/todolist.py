import discord
from discord.ext import commands
from mysql.connector import connect, Error
import datetime
import asyncio
import time

class todolist(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.loop.create_task(self.background_task())

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        channel = reaction.message.channel
        emoji = str(reaction.emoji)
        if user.bot:
            return

        if emoji == "<:deletesign:853677705861267456>" and str(reaction.message.author) == "MyTodoList#7809":
            data = str(reaction.message.content).split("\n")
            for x in range(len(data)):
                data[x] = data[x].split(": ")
            print(data)
            try:
                with connect(
                    host="localhost",
                    user="root",
                    database ="todolistbot",
                ) as connection:
                    search_query = "DELETE FROM task WHERE nama = '{}' AND tanggal = '{}' AND waktu = '{}' ;"\
                        .format(data[0][1], data[1][1], data[2][1])
                    with connection.cursor() as cursor:
                        cursor.execute(search_query)
                        connection.commit()
            except Error as e:
                await channel.send("```Data masih kosong```")
                print(e)
            else:
                msg = await channel.send("```Data berhasil dihapus```")
                time.sleep(5)
                await msg.delete()
        else:
            print("Gagal")

    @commands.command()
    async def help(self, ctx):
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

    @commands.command()
    async def ping(self, ctx):
        # await ctx.send(str(round(self.client.latency * 100)) + "ms")
        ping = str(round(self.client.latency * 100)) + " ms"
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="Ping " + str(ctx.author), value=ping, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def all(self, ctx):
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
                    tanggalwaktu_deadline = datetime.datetime.strptime(tanggalwaktu_deadline, '%d/%m/%Y %H:%M:%S')
                    tanggalwaktu_sekarang = datetime.datetime.now()
                    sisa = str(tanggalwaktu_deadline - tanggalwaktu_sekarang).split()
                    if len(sisa) == 1:
                        sisa_waktu = sisa[0][0:8]
                        await ctx.send("**" + "Task " + str(count) + "**\t(id=" + str(content[0]) + ")")
                        data = await ctx.send("```Nama\t\t\t\t\t\t\t: {}\nTanggal Deadline\t\t\t\t: {}\nWaktu Deadline\t\t\t\t  : {}\nSisa Waktu\t\t\t\t\t  : {}```"\
                            .format(content[1], content[2], content[3], sisa_waktu))
                    else:
                        sisa_hari = sisa[0] + " " + sisa[1]
                        sisa_waktu = sisa[2][0:8]
                        await ctx.send("**" + "Task " + str(count) + "**\t(id=" + str(content[0]) + ")")
                        data = await ctx.send("```Nama\t\t\t\t\t\t\t: {}\nTanggal Deadline\t\t\t\t: {}\nWaktu Deadline\t\t\t\t  : {}\nSisa Waktu\t\t\t\t\t  : {}```"\
                            .format(content[1], content[2], content[3], (sisa_hari + " " + sisa_waktu)))
                    count += 1
                    emoji = "<:deletesign:853677705861267456>"
                    await data.add_reaction(emoji)

    @commands.command()
    async def add(self, ctx, nama, tanggal, waktu):
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

    @commands.command()
    async def update(self, ctx, target, choice, newdata):
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

    @commands.command()
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

    @commands.command()
    async def clear(self, ctx, amount=100):
        channel = ctx.message.channel
        messages = []
        async for message in channel.history(limit=amount + 1):
            messages.append(message)
        await channel.delete_messages(messages)
        msg = await ctx.send('Messaged deleted.')
        time.sleep(5)
        await msg.delete()

    async def reminder(self):
        await self.client.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
        ctx = self.client.get_channel(828984053700362261) # Note: It's more efficient to do bot.get_guild(guild_id).get_channel(channel_id) as there's less looping involved, but just get_channel still works fine
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

    async def background_task(self):
        now = datetime.datetime.now()
        if now.time() > datetime.time(7, 0, 0):  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
            tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
            seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
            await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
        while True:
            now = datetime.datetime.now() # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
            target_time = datetime.datetime.combine(now.date(), datetime.time(7, 0, 0))  # 6:00 PM today (In UTC)
            seconds_until_target = (target_time - now).total_seconds()
            await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
            await self.reminder()  # Call the helper function that sends the message
            tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), time(0))
            seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
            await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start a new iteration
    
def setup(client):
    client.add_cog(todolist(client))