import re
import datetime
import discord
from discord.ext import tasks
from discord.ext import commands

BIRTHDAYS_CHANNEL = 1295579142171000896
BIRTHDAY_ANNOUNCEMENTS = 1295575246455439370

birthdays = {}

async def load_birthdays(bot: commands.Bot):
    channel = bot.get_channel(BIRTHDAYS_CHANNEL)
    if channel is None:
        print("Birthdays channel not found!")
        return

    # Fetch all messages from the birthdays channel
    async for message in channel.history(limit=100):  # Adjust limit as needed
        match = re.search(r'^(<@!?(\d+)>)\'s birthday is on (\d{2}-\d{2}-\d{4}) 🎂$', message.content)
        if match:
            user_id = int(match.group(2))  # Extract user ID
            birthdate = match.group(3)      # Extract birthdate
            birthdays[user_id] = birthdate   # Store in the dictionary

    print("Loaded birthdays:", birthdays)

async def birthday(interaction: discord.Interaction, birthdate: str, bot: commands.Bot):
    try:
        # Ensure correct format
        if len(birthdate) != 10 or birthdate[2] != '-' or birthdate[5] != '-':
            await interaction.response.send_message("Please use the correct format: MM-DD-YYYY.", ephemeral=True)
            return
        
        # Check if the provided date is valid
        month, day, year = birthdate.split('-')
        month = int(month)
        day = int(day)
        year = int(year)
        
        if not (1 <= month <= 12 and 1 <= day <= 31 and year > 1900):
            await interaction.response.send_message("Invalid date provided. Ensure correct ranges.", ephemeral=True)
            return

        # Find the "birthdays" channel by ID
        channel = bot.get_channel(BIRTHDAYS_CHANNEL)

        if channel is None:
            await interaction.response.send_message("Birthdays channel not found!", ephemeral=True)
            return

        await channel.send(f"{interaction.user.mention}'s birthday is on {birthdate} 🎂")
        birthdays[interaction.user.id] = birthdate  # Update the dictionary with the new birthday
        await interaction.response.send_message(f"Your birthday ({birthdate}) has been recorded!", ephemeral=True)

    except ValueError:
        await interaction.response.send_message("Please enter a valid birthdate in MM-DD-YYYY format.", ephemeral=True)

@tasks.loop(hours=24)  # Run this task every 24 hours
async def check_birthdays_func(bot: commands.Bot):
    today = datetime.datetime.now().strftime("%m-%d")
    channel = bot.get_channel(BIRTHDAY_ANNOUNCEMENTS)  # Change to your desired announcements channel

    if channel is None:
        print("Announcements channel not found!")
        return

    for user_id, birthdate in birthdays.items():
        if birthdate[:5] == today:  # Compare only month and day
            user = await bot.fetch_user(user_id)  # Fetch the user object
            await channel.send(f"🎉 Happy Birthday {user.mention}! 🎂 Your birthday is today!")

@check_birthdays_func.before_loop
async def before_check_birthdays(bot: commands.Bot):
    await bot.wait_until_ready()  # Wait until the bot is ready