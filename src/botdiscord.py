import discord
from discord import app_commands
from discord.ext import commands, tasks
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

@tasks.loop(hours=1)  # Check every hour
async def weekly_reset_task():
    """Tự động reset danh sách user vào 6AM sáng thứ 2 hàng tuần GMT+7"""
    try:
        now = datetime.now(GMT_PLUS_7)
        
        # Kiểm tra xem có phải 6AM thứ 2 không (weekday 0 = Monday)
        if now.weekday() == 0 and now.hour == 6 and now.minute < 60:
            logger.info("🔄 Starting weekly user data reset...")
            
            # Reset tất cả user data
            reset_count = user_manager.reset_all_users()
            
            logger.info(f"✅ Weekly reset completed! Cleared {reset_count} user(s) data.")
            
            # Có thể gửi thông báo đến channel cụ thể nếu cần
            # for guild in bot.guilds:
            #     for channel in guild.text_channels:
            #         if channel.name in ["general", "announcements"]:
            #             await channel.send("🔄 **Weekly Reset**: Tất cả danh sách character đã được reset!")
            #             break
                        
    except Exception as e:
        logger.error(f"Error in weekly reset task: {e}")

@weekly_reset_task.before_loop
async def before_weekly_reset():
    """Wait for bot to be ready before starting the task"""
    await bot.wait_until_ready()

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
    
    # Start weekly reset task
    weekly_reset_task.start()
    logger.info("📅 Weekly reset task started (6AM Monday GMT+7)")
    
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
@bot.tree.command(name="ping", description="Check bot latency")
async def ping_slash(interaction: discord.Interaction):
    """Ping command as slash command"""
    if not is_allowed_channel(interaction):
        await interaction.response.send_message("❌ This command can only be used in specific channels.", ephemeral=True)
        return
    
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")

@bot.tree.command(name="hello", description="Get a greeting from the bot")
async def hello_slash(interaction: discord.Interaction):
    """Hello command as slash command"""
    if not is_allowed_channel(interaction):
        await interaction.response.send_message("❌ This command can only be used in specific channels.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"👋 Hello {interaction.user.mention}! Welcome to Dream & Lethe Bot!")

# Slash Commands with Autocomplete
@bot.tree.command(name="rela", description="Assign characters to houses optimally")
async def rela_command(interaction: discord.Interaction, characters: str):
    """Character assignment command - input multiple characters separated by commas"""
    if not is_allowed_channel(interaction):
        await interaction.response.send_message("❌ This command can only be used in specific channels.", ephemeral=True)
        return
    
    # Parse characters from input string (separated by commas)
    character_list = [char.strip() for char in characters.split(',') if char.strip()]
    
    if not character_list:
        await interaction.response.send_message("❌ Please provide at least one character name.\nExample: `/rela Han Wu, Imperial, Weiqing`", ephemeral=True)
        return
    
    # Validate characters exist (case insensitive)
    valid_characters = []
    invalid_characters = []
    
    for char in character_list:
        # Find matching character (case insensitive)
        found = False
        for valid_char in CHARACTERS:
            if char.lower() == valid_char.lower():
                valid_characters.append(valid_char)
                found = True
                break
        if not found:
            invalid_characters.append(char)
    
    if invalid_characters:
        await interaction.response.send_message(f"❌ Invalid characters: {', '.join(invalid_characters)}\nValid characters: {', '.join(CHARACTERS[:10])}...", ephemeral=True)
        return
    
    # Solve house assignment
    try:
        assignment, total_score = solve_house_assignment(valid_characters)
        
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
        await interaction.response.send_message(f"🏠 **Cách xếp mèo:**\n```\n{result_text}\n```")
        
    except Exception as e:
        print(f"Error in house assignment: {e}")
        await interaction.response.send_message("❌ Có lỗi xảy ra khi xử lý phân bổ nhà!", ephemeral=True)

@rela_command.autocomplete('characters')
async def rela_autocomplete(interaction: discord.Interaction, current: str):
    """Simple autocomplete for character selection"""
    try:
        # Very simple: just filter characters by what user typed
        filtered = [
            char for char in CHARACTERS 
            if current.lower() in char.lower()
        ][:25]
        
        return [
            discord.app_commands.Choice(name=char, value=char)
            for char in filtered
        ]
    except:
        # If any error, return empty list
        return []

# User Data Management Commands

@bot.tree.command(name="add", description="Thêm character vào danh sách cá nhân của bạn")
@app_commands.describe(character="Tên character muốn thêm")
async def add_character(interaction: discord.Interaction, character: str):
    """Add character to user's personal list"""
    await interaction.response.defer()
    
    success, message = user_manager.add_character(interaction.user.id, character, CHARACTERS)
    await interaction.followup.send(message)

@add_character.autocomplete('character')
async def add_character_autocomplete(interaction: discord.Interaction, current: str):
    """Autocomplete for add character command - shows characters not yet in user's list"""
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

@bot.tree.command(name="gen", description="Tạo lệnh /rela từ danh sách character cá nhân của bạn")
async def generate_rela(interaction: discord.Interaction):
    """Generate /rela command from user's character list"""
    await interaction.response.defer()
    
    success, result = user_manager.generate_rela_command(interaction.user.id)
    
    if success:
        # Also show user stats
        stats = user_manager.get_user_stats(interaction.user.id)
        message = f"{stats}\n\n**🎮 Copy lệnh này:**\n```{result}```"
    else:
        message = result
    
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

@bot.tree.command(name="resetstatus", description="Kiểm tra trạng thái weekly reset (Admin only)")
async def reset_status(interaction: discord.Interaction):
    """Check weekly reset status"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ This command is for administrators only.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    # Get current time in GMT+7
    now = datetime.now(GMT_PLUS_7)
    total_users = user_manager.get_total_users()
    
    # Calculate next Monday 6AM
    days_until_monday = (7 - now.weekday()) % 7
    if days_until_monday == 0 and now.hour >= 6:
        days_until_monday = 7  # Next week if already past 6AM today
    
    next_reset = now.replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
    
    embed = discord.Embed(title="📅 Weekly Reset Status", color=0x00ff00)
    embed.add_field(name="Current Time (GMT+7)", value=now.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Next Reset", value=next_reset.strftime("%Y-%m-%d %H:%M:%S (Monday)"), inline=False)
    embed.add_field(name="Total Users", value=f"{total_users} users have character data", inline=False)
    embed.add_field(name="Task Status", value="✅ Running" if weekly_reset_task.is_running() else "❌ Stopped", inline=False)
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="forcereset", description="Force reset tất cả user data ngay lập tức (Admin only)")
async def force_reset(interaction: discord.Interaction):
    """Force reset all user data immediately"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ This command is for administrators only.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    # Confirm before reset
    total_users = user_manager.get_total_users()
    
    if total_users == 0:
        await interaction.followup.send("ℹ️ Không có user data nào để reset.")
        return
    
    # Perform reset
    reset_count = user_manager.reset_all_users()
    
    embed = discord.Embed(title="🔄 Force Reset Completed", color=0xff9900)
    embed.add_field(name="Users Cleared", value=f"{reset_count} users", inline=False)
    embed.add_field(name="Time", value=datetime.now(GMT_PLUS_7).strftime("%Y-%m-%d %H:%M:%S GMT+7"), inline=False)
    
    await interaction.followup.send(embed=embed)
    logger.info(f"🔄 Force reset executed by {interaction.user} - cleared {reset_count} users")

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
    finally:
        # Stop the weekly reset task when bot shuts down
        if weekly_reset_task.is_running():
            weekly_reset_task.stop()
            logger.info("📅 Weekly reset task stopped")

if __name__ == "__main__":
    run_bot()
