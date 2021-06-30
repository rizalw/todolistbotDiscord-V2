# todolistbotDiscord-V2
Massive improvement in the background. I'm not using txt anymore for storing data

If you don't know what this apps do. Basicly it's a todolist discord bot that run on python. 

Requirements to run this app:
- Discord.py library
- Datetime Library
- Time Library
- Mysql.connector Library
- Asyncio Library
- OS Library
- Xampp, especially MySQL module

Changelog
=
11/06/2021
===
What's New:
- Create add feature
- Create delete feature
- Create clear feature
- Create ping feature
- Create update feature

12/06/2021
===
What's New:
- Create reminder feature
- Cogs!!!

17/06/2021
===
What's New:
- New reaction feature!!! 
(You dont have to write t!delete anymore to delete task, just use reaction that will be available everytime you send t!all)
- User cant add the same task anymore (It means user can't add new task that already inserted before. Bot will compare title, date and time to every task in database)
- A bug fixed (It appears when the remaining time below 1 days)

18/06/2021
===
What's New:
- Another server can't see the task that inserted from another server (e.g Task that inserted from Server A can't be accessed from Server B using command t!all)
- Disable Update and Delete feature (Because updating task is more time consuming than reinsert task and if you want to delete task just use "X" reaction below respective task)
- Create datetime verification to ensure every input from user is feasible to be converted to datetime datatype (If the user has the wrong input, the bot will tell the correct format)

21/06/2021
===
What's New:
- Change help command for better clarity
- Some minor changes

25/06/2021
===
What's New:
- Some minor optimization
