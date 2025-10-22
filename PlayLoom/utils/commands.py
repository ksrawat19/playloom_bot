from PlayLoom.utils.logger import logger
from PlayLoom.vars import Var

def get_commands():
    from pyrogram.types import BotCommand  # ✅ Deferred import

    command_descriptions = {
        "start": "Start the bot and get a welcome message",
        "link": "(Group) Generate a direct link for a file or batch",
        "dc": "Retrieve the data center (DC) information of a user or file",
        "ping": "Check the bot's status and response time",
        "about": "Get information about the bot",
        "help": "Show help and usage instructions",
        "status": "(Admin) View bot details and current workload",
        "stats": "(Admin) View usage statistics and resource consumption",
        "broadcast": "(Admin) Send a message to all users",
        "ban": "(Admin) Ban a user",
        "unban": "(Admin) Unban a user",
        "log": "(Admin) Send bot logs",
        "restart": "(Admin) Restart the bot",
        "shell": "(Admin) Execute a shell command",
        "users": "(Admin) Show the total number of users",
        "authorize": "(Admin) Grant permanent access to a user",
        "deauthorize": "(Admin) Remove permanent access from a user",
        "listauth": "(Admin) List all authorized users"
    }
    return [BotCommand(name, desc) for name, desc in command_descriptions.items()]

async def set_commands():
    if Var.SET_COMMANDS:
        try:
            from PlayLoom.bot import StreamBot  # ✅ Import here to ensure it's initialized
            commands = get_commands()
            if commands and StreamBot:
                await StreamBot.set_bot_commands(commands)
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}", exc_info=True)
