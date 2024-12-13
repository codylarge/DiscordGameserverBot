import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime
import os
import asyncio
from dotenv import load_dotenv
from utils import is_valid_profile_link
from birthdays import birthday, check_birthdays_func, load_birthdays

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
commands_synced = False

bot = commands.Bot(command_prefix="!", intents=intents)

MY_SERVER = discord.Object(id=1290215447530307665) 

REPORTS_CHANNEL_ID = 1293061739755081738 

VERIFIED_ROLE_NAME = "Verified" 
VERIFIED_USERS_CHANNEL = 1295579039184195634
verified_users = {}

TICKETS_CHANNEL_ID = 1293441350296932392

BIRTHDAYS_CHANNEL = 1295579142171000896
BIRTHDAY_ANNOUNCEMENTS = 1295575246455439370

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    
    await load_birthdays(bot)
    print('------')

    guild = MY_SERVER 
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} commands in server {guild.id}.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# /verify
@bot.tree.command(name="verify", description="Verify a Steam64/Profile link", guild=MY_SERVER)
@app_commands.describe(profile_link="The user's Steam64 ID or Profile Link")
async def verify(interaction: discord.Interaction, profile_link: str):
    verified_role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE_NAME) 

    # Check if the profile link is valid
    if not is_valid_profile_link(profile_link):
        await interaction.response.send_message(
            "Error: The provided profile link is invalid. Please provide a valid Steam64 ID or a valid Steam profile link.",
            ephemeral=True
        )
        return

    # Assign the verified role to the user
    if verified_role:
        await interaction.user.add_roles(verified_role)  # Assign verified role

        # Send a message to the verified-users channel
        verified_users_channel = bot.get_channel(VERIFIED_USERS_CHANNEL)
        if verified_users_channel:
            verified_message = (
                f"**User Verified:** {interaction.user.mention}\n"
                f"**Profile Link:** {profile_link}"
            )
            await verified_users_channel.send(verified_message)

        await interaction.response.send_message(
            f"Thank you! You've been verified with the profile link `{profile_link}`. "
            f"You have been given the `{VERIFIED_ROLE_NAME}` role.",
            ephemeral=True
        )

    else:  # Edge case: Verified role not found
        await interaction.response.send_message(
            f"Error: Could not find the `{VERIFIED_ROLE_NAME}` role.",
            ephemeral=True
        )


@bot.tree.command(name="addverified", description="Manually add a verified user", guild=MY_SERVER)
@app_commands.describe(username="The Discord username of the user", profile_link="The user's Steam64 ID or Profile Link", date="The date of verification (any string)")
@commands.has_permissions(administrator=True)  # Ensure the user is an admin
async def add_verified(interaction: discord.Interaction, username: str, profile_link: str, date: str):
    # Search for the user in the guild by username
    user_mention = None
    for member in interaction.guild.members:
        if member.name == username:  # Check for the username match
            user_mention = member
            break

    if user_mention is None:
        await interaction.response.send_message("Error: Could not find the specified user.", ephemeral=True)
        return

    verified_role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE_NAME)

    # Assign the verified role to the user
    if verified_role:
        await user_mention.add_roles(verified_role)  # Assign verified role

        # Send a message to the verified-users channel
        verified_users_channel = bot.get_channel(VERIFIED_USERS_CHANNEL)  # Replace with your channel ID
        if verified_users_channel:
            verified_message = (
                f"**User Verified by Admin:** {user_mention.mention}\n"
                f"**Profile Link:** {profile_link}\n"
                f"**Date of Verification:** {date}"
            )
            await verified_users_channel.send(verified_message)

        await interaction.response.send_message(
            f"Successfully verified {user_mention.mention} with the profile link `{profile_link}` on {date}.",
            ephemeral=True
        )
    else:  # Edge case: Verified role not found
        await interaction.response.send_message(
            f"Error: Could not find the `{VERIFIED_ROLE_NAME}` role.",
            ephemeral=True
        )


# /report
@bot.tree.command(name="report", description="Report a player by name/Steam64 and specify a reason", guild=MY_SERVER)
@app_commands.describe(name="The player's name or Steam64 ID", reason="The reason for reporting")
async def report(interaction: discord.Interaction, name: str, reason: str):
    await interaction.response.send_message(f"Thank you for reporting! The player `{name}` has been reported for `{reason}`.", ephemeral=True) # Acknowledge the command

    report_channel = bot.get_channel(REPORTS_CHANNEL_ID) 

    if report_channel:
        report_message = (
            f"**Reported by:** {interaction.user.mention}\n"
            f"**Player:** {name}\n"
            f"**Reason:** {reason}\n"
            f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        await report_channel.send(report_message)
    else:
        await interaction.followup.send("Error: Could not find the reports channel", ephemeral=True)

# /ticket
@bot.tree.command(name="ticket", description="Submit a ticket to the server owner", guild=MY_SERVER)
@app_commands.describe(message="Why are you creating a ticket?")
async def ticket(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("Your ticket has been submitted.", ephemeral=True) # Acknowledge the command

    report_channel = bot.get_channel(TICKETS_CHANNEL_ID) 

    if report_channel:
        report_message = (
            f"**Ticket created by:** {interaction.user.mention}\n"
            f"**Message:** {message}\n"
            f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        await report_channel.send(report_message)
    else:
        await interaction.followup.send("Error: Could not find the reports channel", ephemeral=True)

# Clear Channel
@bot.tree.command(name="clearchannel", description="Clear all messages from the current channel.", guild=MY_SERVER)
async def clearchannel(interaction: discord.Interaction):
    # Check permissions, etc.
    try:
        # Process deletion in batches
        deleted = await interaction.channel.purge(limit=100)
        await asyncio.sleep(1)  # Delay between batches to avoid hitting the rate limit
        # Continue if more messages exist
    except discord.errors.HTTPException:
        await asyncio.sleep(5)  # Extra delay if hitting rate limits




# -------------------- Birthday Commands --------------------
@bot.tree.command(name="birthday", description="Register your birthday")
@app_commands.describe(birthdate="Your birthdate in MM-DD-YYYY format")
async def birthday_command(interaction: discord.Interaction, birthdate: str):
    await birthday(interaction, birthdate, bot)  # Await the birthday function here

@tasks.loop(hours=24)
async def check_birthdays():
    await check_birthdays_func(bot)


@bot.tree.command(name="say", description="Repeat what you say", guild=MY_SERVER)
@app_commands.describe(message="The message you want the bot to say")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

bot.run(TOKEN)
