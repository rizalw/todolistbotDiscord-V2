import discord
from discord.ext import commands
from discord.ext.commands.core import command
from mysql.connector import connect, Error, cursor
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
                    search_query = "DELETE FROM task WHERE nama = '{}' AND tanggal = '{}' AND waktu = '{}' AND id_server = '{}';"\
                        .format(data[0][1], data[1][1], data[2][1], str(channel.guild.id))
                    with connection.cursor() as cursor:
                        cursor.execute(search_query)
                        connection.commit()
            except Error as e:
                await channel.send("```Data masih kosong```")
                print(e)
            else:
                await channel.send("```Data berhasil dihapus```")
        else:
            print("Gagal")

    @commands.command()
    async def help(self, ctx, *choice):
        if len(choice) == 0:
            embed=discord.Embed(title="Todolist Commands", color=0xff0000)
            embed.add_field(name="List of Features", value="t!help features", inline=True)
            embed.add_field(name="List of Commands", value="t!help commands", inline=True)
            embed.set_footer(text="by MyTodoList")
            await ctx.send(embed=embed)
        elif len(choice) == 1:
            pilihan = choice[0]
            if pilihan == "features":
                embed=discord.Embed(title="List of Features", color=0xff0000)
                embed.add_field(name="Annual Reminder", value="Every 08.00 a.m this bot will send to do list to spesific text channel in spesific server. (I planned to make this feature more flexible)", inline=False)
                embed.add_field(name="Store Tasks Data", value="This bot can store your task into to do list", inline=False)
                embed.add_field(name="Isolated To Do List", value="Data that inserted from server A can't be accessed from server B", inline=False)
                embed.add_field(name="Simple Way of Deleting Task From To Do List", value="If you want to delete a task, just click 'x' reaction below the task that you want to delete", inline=False)
                embed.set_footer(text="by MyTodoList")
                await ctx.send(embed=embed)
            elif pilihan == "commands":
                embed=discord.Embed(title="List of Commands", color=0xff0000)
                embed.add_field(name="Insert New Task", value="t!add contoh_task 12/05/2021 23:59:00", inline=True)
                embed.add_field(name="See All Tasks", value="t!all", inline=True)
                embed.add_field(name="Check Your Ping", value="t!ping", inline=False)
                embed.add_field(name="Delete Messages Above You", value="t!delete 0 (Specified how many message do you want to delete)", inline=False)
                embed.set_footer(text="by MyTodoList")
                await ctx.send(embed=embed)
        else:
            await ctx.send("Command yang dimasukkan salah")        

    @commands.command()
    async def ping(self, ctx):
        # await ctx.send(str(round(self.client.latency * 100)) + "ms")
        ping = str(round(self.client.latency * 100)) + " ms"
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="Ping " + str(ctx.author), value=ping, inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(pass_context = True)
    async def add(self, ctx, nama, tanggal, waktu):
        id_server = str(ctx.guild.id)
        try:
            datetime.datetime.strptime(tanggal + " " + waktu, '%d/%m/%Y %H:%M:%S')
        except:
            await ctx.send("Format tanggal/waktu salah.\nContoh: t!add nama_tugas 25/05/2021 23:59:99")
        else:
            try:
                with connect(
                    host="localhost",
                    user="root",
                    database ="todolistbot",
                ) as connection:
                    with connection.cursor() as cursor:
                        check_query = "SELECT nama FROM task WHERE nama = '{}' AND tanggal = '{}' AND waktu = '{}' AND id_server = '{}';".format(nama, tanggal, waktu, id_server)
                        cursor.execute(check_query)
                        result = cursor.fetchall()
                        if result:
                            await ctx.send("Data sudah pernah dimasukkan, jika ingin mengubah silahkan gunakan t!update sesuai dengan panduan di dalam t!help")
                        else:
                            add_task_query = """
                        INSERT INTO task (nama, tanggal, waktu, id_server) VALUES 
                        ("{}", "{}", "{}", "{}");""".format(nama, tanggal, waktu, id_server)
                            cursor.execute(add_task_query)
                            connection.commit()
                            await ctx.send("Data telah dimasukkan")

            except Error as e:
                print(e)
                await ctx.send("Input Gagal")

    @commands.command(pass_context = True)
    async def all(self, ctx):
        id_server = str(ctx.guild.id)
        try:
            with connect(
                host="localhost",
                user="root",
                database ="todolistbot",
            ) as connection:
                all_query = "SELECT * FROM task WHERE id_server = '{}' ORDER BY id ASC;".format(id_server)
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
                for content in result:
                    if count == 1:
                        await ctx.send("**Daftar Tugas** for @everyone")
                    tanggalwaktu_deadline = content[2] + " " + content[3]
                    tanggalwaktu_deadline = datetime.datetime.strptime(tanggalwaktu_deadline, '%d/%m/%Y %H:%M:%S')
                    tanggalwaktu_sekarang = datetime.datetime.now()
                    sisa = str(tanggalwaktu_deadline - tanggalwaktu_sekarang  - datetime.timedelta(hours = 7)).split()
                    if len(sisa) == 1:
                        sisa_waktu = sisa[0][0:8]
                        await ctx.send("**" + "Task " + str(count) + "**")
                        data = await ctx.send("```Nama\t\t\t\t\t\t\t: {}\nTanggal Deadline\t\t\t\t: {}\nWaktu Deadline\t\t\t\t  : {}\nSisa Waktu\t\t\t\t\t  : {}```"\
                            .format(content[1], content[2], content[3], sisa_waktu))
                    else:
                        sisa_hari = sisa[0] + " " + sisa[1]
                        sisa_waktu = sisa[2][0:8]
                        await ctx.send("**" + "Task " + str(count) + "**")
                        data = await ctx.send("```Nama\t\t\t\t\t\t\t: {}\nTanggal Deadline\t\t\t\t: {}\nWaktu Deadline\t\t\t\t  : {}\nSisa Waktu\t\t\t\t\t  : {}```"\
                            .format(content[1], content[2], content[3], (sisa_hari + " " + sisa_waktu)))
                    count += 1
                    emoji = "<:deletesign:853677705861267456>"
                    await data.add_reaction(emoji)


    # @commands.command()
    # async def update(self, ctx, target, choice, newdata):
    #     try:
    #         with connect(
    #             host="localhost",
    #             user="root",
    #             database ="todolistbot",
    #         ) as connection:
    #             if choice == "nama":
    #                 alter_query = "UPDATE task SET nama = '{}' where id = {};".format(newdata, target)
    #             elif choice == "tanggal":
    #                 alter_query = "UPDATE task SET tanggal = '{}' where id = {};".format(newdata, target)
    #             elif choice == "waktu":
    #                 alter_query = "UPDATE task SET waktu = '{}' where id = {};".format(newdata, target)
    #             with connection.cursor() as cursor:
    #                 cursor.execute(alter_query)
    #                 connection.commit()
                
    #     except Error as e:
    #         print(e)
    #         await ctx.send("Update Gagal")
    #     else:
    #         await ctx.send("Data telah diupdate")

    # @commands.command()
    # async def delete(ctx, id):
    #     try:
    #         with connect(
    #             host="localhost",
    #             user="root",
    #             database ="todolistbot",
    #         ) as connection:
    #             delete_task_query = "DELETE FROM task WHERE id = {};".format(id)
    #             with connection.cursor() as cursor:
    #                 cursor.execute(delete_task_query)
    #                 connection.commit()
    #     except Error as e:
    #         print(e)
    #         await ctx.send("Hapus Gagal")
    #     else:
    #         await ctx.send("Data telah dihapus")

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
    
    @commands.command(pass_context = True)
    async def register_reminder(self, ctx):
        id_server = str(ctx.guild.id)
        channel_name = str(ctx.channel)
        try:
            with connect(
                host="localhost",
                user="root",
                database ="todolistbot",
            ) as connection:
                with connection.cursor() as cursor:
                    register_query = "INSERT INTO guild_reminder (id_server, channel_name) VALUES ('{}', '{}');"\
                            .format(id_server, channel_name)
                    cursor.execute(register_query)
                    connection.commit()
        except Error as e:
            print(e)
            await ctx.send("Pendaftaran gagal")
        else:
            await ctx.send("Pendaftaran berhasil")

    #AWALNYA MAU ADA FITUR DYNAMIC REMINDER, JADI GAK CUMAN DI SATU TEXT CHANNEL AJA, BISA FLEXIBLE SESUAI DENGAN APA YANG DIREGISTER CUMAN GAGAL
    async def reminder(self):
        await self.client.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
        ctx = self.client.get_channel(826314501157814285) # Note: It's more efficient to do bot.get_guild(guild_id).get_channel(channel_id) as there's less looping involved, but just get_channel still works fine
        try:
            with connect(
                host="localhost",
                user="root",
                database ="todolistbot",
            ) as connection:
                all_query = "SELECT nama, tanggal, waktu, id_server FROM task;"
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
                # for x in range(len(id_server)):
                    # server = discord.Guild
                    # server.id = int(id_server[x])
                    # channel_id = discord.utils.get(server.channels, name=str(channel_name[x]), type="discord.ChannelType.text") 
                    # channel = self.client.get_channel(int(channel_id))
                count = 1
                await ctx.send("**REMAINDER!!!**")
                for content in result:
                    # if content[3] == str(id_server[x]):
                    tanggalwaktu_deadline = content[1] + " " + content[2]
                    tanggalwaktu_deadline = datetime.datetime.strptime(tanggalwaktu_deadline, '%d/%m/%Y %H:%M:%S')
                    tanggalwaktu_sekarang = datetime.datetime.now()
                    sisa = str(tanggalwaktu_deadline - tanggalwaktu_sekarang  - datetime.timedelta(hours = 7)).split()
                    if count == 1:
                        await ctx.send("**Daftar Tugas** for @everyone")
                    if len(sisa) == 1:
                        sisa_waktu = sisa[0][0:8]
                        await ctx.send("**" + "Task " + str(count) + "**")
                        data = await ctx.send("```Nama\t\t\t\t\t\t\t: {}\nTanggal Deadline\t\t\t\t: {}\nWaktu Deadline\t\t\t\t  : {}\nSisa Waktu\t\t\t\t\t  : {}```"\
                            .format(content[0], content[1], content[2], sisa_waktu))
                    else:
                        sisa_hari = sisa[0] + " " + sisa[1]
                        sisa_waktu = sisa[2][0:8]
                        await ctx.send("**" + "Task " + str(count) + "**")
                        data = await ctx.send("```Nama\t\t\t\t\t\t\t: {}\nTanggal Deadline\t\t\t\t: {}\nWaktu Deadline\t\t\t\t  : {}\nSisa Waktu\t\t\t\t\t  : {}```"\
                            .format(content[0], content[1], content[2], (sisa_hari + " " + sisa_waktu)))
                    count += 1                    
                    
    async def background_task(self):
        try:
            with connect(
                host="localhost",
                user="root",
                database ="todolistbot",
            ) as connection:
                with connection.cursor() as cursor:
                    # get_reminder = "SELECT id_server, channel_name FROM guild_reminder;"
                    # cursor.execute(get_reminder)
                    # result = cursor.fetchall()
                    pass
        except Error as e:
            print(e)
        else:
            # id_server = []
            # channel_name = []
            # for x in result:
            #     id_server.append(x[0])
            #     channel_name.append(x[1])
            now = datetime.datetime.now()
            if now.time() > datetime.time(23, 33, 0):  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
                tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
                seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
                await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
            while True:
                now = datetime.datetime.now() # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
                target_time = datetime.datetime.combine(now.date(), datetime.time(23, 33, 0))  # 6:00 PM today (In UTC)
                seconds_until_target = (target_time - now).total_seconds()
                await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
                await self.reminder()  # Call the helper function that sends the message
                tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0))
                seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
                await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start a new iteration
    
def setup(client):
    client.add_cog(todolist(client))