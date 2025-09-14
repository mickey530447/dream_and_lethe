import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add the parent directory to the path to import constants
sys.path.append(str(Path(__file__).parent.parent))
from constants.bot_constants import CHARACTERS, RELATIONSHIPS
from solver import HouseAssignmentSolver
from user_manager import UserDataManager

# Import solver functions
try:
    from solver import solve_house_assignment, format_assignment_result
except ImportError:
    print("Could not import solver - house assignment will not work")
    def solve_house_assignment(people_list):
        return None, 0
    def format_assignment_result(assignment, score):
        return "Solver not available"

# Load environment variables
load_dotenv()

# Bot configuration
ALLOWED_CHANNEL_NAMES = []  # Empty list means all channels allowed

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
# Comment out privileged intents if not enabled in developer portal
# intents.message_content = True  # Privileged intent
# intents.members = True          # Privileged intent
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)
# Get the parent directory of src folder for user_data
user_data_path = Path(__file__).parent.parent / "user_data"
user_manager = UserDataManager(data_dir=str(user_data_path))

def is_allowed_channel(interaction_or_ctx):
    """Check if command is used in an allowed channel"""
    # Get channel from interaction or context
    if hasattr(interaction_or_ctx, 'channel'):
        channel = interaction_or_ctx.channel
    elif hasattr(interaction_or_ctx, 'interaction'):
        channel = interaction_or_ctx.interaction.channel
    else:
        return False
    
    # If no restrictions set, allow all channels
    if not ALLOWED_CHANNEL_NAMES:
        return True
    
    # Check by channel name
    if channel.name in ALLOWED_CHANNEL_NAMES:
        return True
    
    return False

# GMT+7 timezone
GMT_PLUS_7 = timezone(timedelta(hours=7))

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
    
    # Set bot activity status
    activity = discord.Game(name="Dream & Lethe Bot")
    await bot.change_presence(activity=activity)

@bot.event
async def on_message(message):
    """Event triggered when a message is sent"""
    # Don't respond to bot's own messages
    if message.author == bot.user:
        return
    
    # No need to process prefix commands if only using slash commands
    # await bot.process_commands(message)

# Slash Commands
@bot.tree.command(name="rela", description="Assign your personal characters to houses optimally")
async def rela_command(interaction: discord.Interaction):
    """Character assignment command - uses your personal character list"""
    if not is_allowed_channel(interaction):
        await interaction.response.send_message("❌ This command can only be used in specific channels.", ephemeral=True)
        return
    
    # Get user's character list
    user_characters = user_manager.get_user_characters(interaction.user.id)
    
    if not user_characters:
        await interaction.response.send_message("❌ You don't have any characters added!\nUse `/add` to add characters first.\nExample: `/add character1:Han Wu character2:Imperial`", ephemeral=True)
        return
    
    # Defer response to prevent Discord timeout (3 seconds)
    await interaction.response.defer()
    
    # Solve house assignment
    try:
        assignment, total_score = solve_house_assignment(user_characters)
        
        # Format result exactly as requested
        result_lines = []
        for house in assignment:
            if house:
                result_lines.append(", ".join(house))
            else:
                result_lines.append("(trống)")
        
        result_lines.append(f"Tổng relationships = {total_score}")
        result_text = "\n".join(result_lines)
        
        # Send result in code block for clean formatting
        await interaction.followup.send(f"🏠 **Cách xếp mèo:**\n```\n{result_text}\n```")
        
    except Exception as e:
        print(f"Error in house assignment: {e}")
        await interaction.followup.send("❌ Có lỗi xảy ra khi xử lý phân bổ nhà!")

# User Data Management Commands

@bot.tree.command(name="add", description="Thêm characters vào danh sách cá nhân của bạn (tối đa 10)")
@app_commands.describe(
    character1="Character thứ 1",
    character2="Character thứ 2 (optional)",
    character3="Character thứ 3 (optional)",
    character4="Character thứ 4 (optional)",
    character5="Character thứ 5 (optional)",
    character6="Character thứ 6 (optional)",
    character7="Character thứ 7 (optional)",
    character8="Character thứ 8 (optional)",
    character9="Character thứ 9 (optional)",
    character10="Character thứ 10 (optional)"
)
async def add_characters(
    interaction: discord.Interaction, 
    character1: str,
    character2: str = None,
    character3: str = None,
    character4: str = None,
    character5: str = None,
    character6: str = None,
    character7: str = None,
    character8: str = None,
    character9: str = None,
    character10: str = None
):
    """Add multiple characters to user's personal list"""
    await interaction.response.defer()
    
    # Collect all non-None characters
    characters_to_add = [char for char in [
        character1, character2, character3, character4, character5,
        character6, character7, character8, character9, character10
    ] if char is not None]
    
    if not characters_to_add:
        await interaction.followup.send("❌ Vui lòng nhập ít nhất 1 character!")
        return
    
    # Add each character and collect results
    results = []
    success_count = 0
    
    for char in characters_to_add:
        success, message = user_manager.add_character(interaction.user.id, char, CHARACTERS)
        if success:
            success_count += 1
            results.append(f"✅ {char}")
        else:
            results.append(f"❌ {char} - {message.split('❌ ')[1] if '❌ ' in message else message}")
    
    # Format response
    response = f"**Kết quả thêm {len(characters_to_add)} characters:**\n\n"
    response += "\n".join(results)
    response += f"\n\n**Tổng kết:** {success_count}/{len(characters_to_add)} thành công"
    
    await interaction.followup.send(response)

# Autocomplete functions for each parameter
async def get_available_characters_for_user(interaction: discord.Interaction, current: str):
    """Helper function to get available characters for autocomplete"""
    try:
        # Get user's current characters
        user_chars = user_manager.get_user_characters(interaction.user.id)
        
        # Get characters not in user's list
        available_chars = [char for char in CHARACTERS if char not in user_chars]
        
        if not current:
            return [
                discord.app_commands.Choice(name=char, value=char)
                for char in available_chars[:25]
            ]
        
        filtered = [
            char for char in available_chars 
            if current.lower() in char.lower()
        ][:25]
        
        return [
            discord.app_commands.Choice(name=char, value=char)
            for char in filtered
        ]
    except:
        return []

@add_characters.autocomplete('character1')
async def add_character1_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@add_characters.autocomplete('character2')
async def add_character2_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@add_characters.autocomplete('character3')
async def add_character3_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@add_characters.autocomplete('character4')
async def add_character4_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@add_characters.autocomplete('character5')
async def add_character5_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@add_characters.autocomplete('character6')
async def add_character6_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@add_characters.autocomplete('character7')
async def add_character7_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@add_characters.autocomplete('character8')
async def add_character8_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@add_characters.autocomplete('character9')
async def add_character9_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@add_characters.autocomplete('character10')
async def add_character10_autocomplete(interaction: discord.Interaction, current: str):
    return await get_available_characters_for_user(interaction, current)

@bot.tree.command(name="remove", description="Xóa character khỏi danh sách cá nhân của bạn")
@app_commands.describe(character="Tên character muốn xóa")
async def remove_character(interaction: discord.Interaction, character: str):
    """Remove character from user's personal list"""
    await interaction.response.defer()
    
    success, message = user_manager.remove_character(interaction.user.id, character)
    await interaction.followup.send(message)

@remove_character.autocomplete('character')
async def remove_character_autocomplete(interaction: discord.Interaction, current: str):
    """Autocomplete for remove character command - shows only user's characters"""
    try:
        user_chars = user_manager.get_user_characters(interaction.user.id)
        
        if not current:
            return [
                discord.app_commands.Choice(name=char, value=char)
                for char in user_chars[:25]
            ]
        
        filtered = [
            char for char in user_chars 
            if current.lower() in char.lower()
        ][:25]
        
        return [
            discord.app_commands.Choice(name=char, value=char)
            for char in filtered
        ]
    except:
        return []

@bot.tree.command(name="clear", description="Xóa toàn bộ danh sách character cá nhân của bạn")
async def clear_user_data(interaction: discord.Interaction):
    """Clear all user data"""
    await interaction.response.defer()
    
    success, message = user_manager.clear_user_data(interaction.user.id)
    await interaction.followup.send(message)

@bot.tree.command(name="check", description="Kiểm tra danh sách character cá nhân của bạn")
async def check_characters(interaction: discord.Interaction):
    """Check user's character list"""
    await interaction.response.defer()
    
    stats = user_manager.get_user_stats(interaction.user.id)
    await interaction.followup.send(stats)

@bot.tree.command(name="list", description="Xem danh sách character cá nhân của bạn")
async def list_characters(interaction: discord.Interaction):
    """Show user's character list"""
    await interaction.response.defer()
    
    stats = user_manager.get_user_stats(interaction.user.id)
    await interaction.followup.send(stats)

# Admin command to check current channel info
@bot.tree.command(name="channelinfo", description="Get current channel information (Admin only)")
async def channel_info(interaction: discord.Interaction):
    """Get channel info for setup purposes"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ This command is for administrators only.", ephemeral=True)
        return
    
    channel = interaction.channel
    embed = discord.Embed(title="Channel Information", color=0x00ff00)
    embed.add_field(name="Channel Name", value=channel.name, inline=False)
    embed.add_field(name="Is Allowed", value="✅ Yes" if is_allowed_channel(interaction) else "❌ No", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `!help` to see available commands.")
    else:
        logger.error(f"An error occurred: {error}")
        await ctx.send("An error occurred while processing the command.")

def run_bot():
    """Run the Discord bot"""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        return
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid token provided!")
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")

if __name__ == "__main__":
    run_bot()
