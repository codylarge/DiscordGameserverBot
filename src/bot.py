import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import os
from dotenv import load_dotenv
from utils import load_verified_users, save_verified_user, is_valid_profile_link

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

MY_SERVER = discord.Object(id=1290215447530307665) 

REPORTS_CHANNEL_ID = 1293061739755081738 

VERIFIED_ROLE_NAME = "Verified" 
VERIFY_CHANNEL_ID = 1293333813182599188
VERIFIED_USERS_FILE = "data/verified_users.txt"
verified_users = {}

TICKETS_CHANNEL_ID = 1293441350296932392

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    load_verified_users(VERIFIED_USERS_FILE, verified_users)
    print(f"Verified users loaded from file.")
    try:
        await bot.tree.sync(guild=MY_SERVER)
        print("Commands synced successfully")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# /verify
@bot.tree.command(name="verify", description="Verify a Steam64/Profile link", guild=MY_SERVER)
@app_commands.describe(profile_link="The user's Steam64 ID or Profile Link")
async def verify(interaction: discord.Interaction, profile_link: str):
    username = interaction.user.name 
    verified_role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE_NAME) 

    # Check if the profile link is valid
    if not is_valid_profile_link(profile_link):
        await interaction.response.send_message(
            "Error: The provided profile link is invalid. Please provide a valid Steam64 ID or a valid Steam profile link.",
            ephemeral=True
        )
        return

    # Check if the user is already verified
    if username in verified_users:
        await interaction.user.add_roles(verified_role),  # Assign verified role just in case
        await interaction.response.send_message(
            f"You have already been verified with the profile link `{verified_users[username][0]}`.",
            ephemeral=True
        )
        return

    # YYYY-MM-DD
    verification_date = datetime.now().strftime("%Y-%m-%d")

    # Add user to the verified list and save to file
    verified_users[username] = (profile_link, verification_date)
    save_verified_user(username, profile_link, VERIFIED_USERS_FILE, verification_date)

    # Assign the verified role to the user
    if verified_role:
        await interaction.user.add_roles(verified_role)  # Assign verified role
        await interaction.response.send_message(
            f"Thank you! You've been verified with the profile link `{profile_link}` on {verification_date}. "
            f"You have been given the `{VERIFIED_ROLE_NAME}` role.",
            ephemeral=True
        )
    else: # Edge case: Verified role not found
        await interaction.response.send_message(
            f"Thank you! You've been verified with the profile link `{profile_link}` on {verification_date}. "
            f"However, I could not find the `{VERIFIED_ROLE_NAME}` role.",
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
async def report(interaction: discord.Interaction, message: str):
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


bot.run(TOKEN)
