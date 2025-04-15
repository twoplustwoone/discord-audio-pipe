import logging
import os
import sys
import traceback

# Configure logging first
def setup_logging(verbose=False):
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Base logger for all errors
    base_logger = logging.getLogger()
    base_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Error log file handler
    error_handler = logging.FileHandler(
        "logs/DAP_errors.log", 
        delay=True,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s\n%(pathname)s:%(lineno)d\n%(exc_info)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    error_handler.setFormatter(error_formatter)
    base_logger.addHandler(error_handler)
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    base_logger.addHandler(console_handler)
    
    # Debug log file if verbose mode
    if verbose:
        debug_handler = logging.FileHandler(
            "logs/discord.log",
            encoding='utf-8',
            mode='w'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        debug_handler.setFormatter(debug_formatter)
        debug_logger = logging.getLogger("discord")
        debug_logger.setLevel(logging.DEBUG)
        debug_logger.addHandler(debug_handler)
    
    return base_logger

# Import other modules after logging setup
import cli
import sound
import asyncio
import discord
import argparse

def load_opus_library():
    """Attempt to load the Opus library with proper error handling."""
    try:
        # Try to load Opus from Homebrew installation
        opus_paths = [
            "/opt/homebrew/lib/libopus.dylib",  # Apple Silicon
            "/usr/local/lib/libopus.dylib",     # Intel Mac
            "/usr/lib/libopus.dylib"            # System default
        ]
        
        for path in opus_paths:
            if os.path.exists(path):
                logging.info(f"Found Opus library at: {path}")
                discord.opus.load_opus(path)
                return True
        
        raise FileNotFoundError("Could not find Opus library in any standard location")
        
    except Exception as e:
        logging.error(f"Failed to load Opus library: {e}")
        logging.error("Please ensure Opus is installed via Homebrew: 'brew install opus'")
        return False

# Parse command line arguments
parser = argparse.ArgumentParser(description="Discord Audio Pipe")
connect = parser.add_argument_group("Command Line Mode")
query = parser.add_argument_group("Queries")

parser.add_argument(
    "-t", "--token",
    dest="token",
    action="store",
    default=None,
    help="The token for the bot"
)

parser.add_argument(
    "-v", "--verbose",
    dest="verbose",
    action="store_true",
    help="Enable verbose logging"
)

connect.add_argument(
    "-c", "--channel",
    dest="channel",
    action="store",
    type=int,
    help="The channel to connect to as an id"
)

connect.add_argument(
    "-d", "--device",
    dest="device",
    action="store",
    type=int,
    help="The device to listen from as an index"
)

query.add_argument(
    "-D", "--devices",
    dest="query",
    action="store_true",
    help="Query compatible audio devices"
)

query.add_argument(
    "-C", "--channels",
    dest="online",
    action="store_true",
    help="Query servers and channels (requires token)"
)

args = parser.parse_args()
is_gui = not any([args.channel, args.device, args.query, args.online])

# Setup logging based on verbosity
logger = setup_logging(args.verbose)

# Initialize Opus library
if not load_opus_library():
    sys.exit(1)

# don't import qt stuff if not using gui
if is_gui:
    import gui
    from PyQt5.QtWidgets import QApplication, QMessageBox

    app = QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

async def main(bot):
    try:
        # query devices
        if args.query:
            logger.info("Querying audio devices...")
            for device, index in sound.query_devices().items():
                print(index, device)
            return

        # check for token
        token = args.token
        if token is None:
            try:
                with open("token.txt", "r") as f:
                    token = f.read().strip()
                logger.info("Token loaded from token.txt")
            except FileNotFoundError:
                logger.error("No token provided and token.txt not found")
                if is_gui:
                    msg.setWindowTitle("Token Error")
                    msg.setText("No Token Provided")
                    msg.exec()
                else:
                    print("No Token Provided")
                return

        # query servers and channels
        if args.online:
            logger.info("Querying servers and channels...")
            await cli.query(bot, token)
            return

        # GUI
        if is_gui:
            logger.info("Starting GUI mode...")
            bot_ui = gui.GUI(app, bot)
            asyncio.ensure_future(bot_ui.ready())
            asyncio.ensure_future(bot_ui.run_Qt())

        # CLI
        else:
            logger.info("Starting CLI mode...")
            asyncio.ensure_future(cli.connect(bot, args.device, args.channel))

        logger.info("Starting bot...")
        await bot.start(token)

    except discord.errors.LoginFailure:
        logger.error("Login failed: Invalid token provided")
        if is_gui:
            msg.setWindowTitle("Login Failed")
            msg.setText("Please check if the token is correct")
            msg.exec()
        else:
            print("Login Failed: Please check if the token is correct")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())

# run program
logger.info("Initializing Discord client...")
bot = discord.Client(intents=discord.Intents.default())
loop = asyncio.get_event_loop_policy().get_event_loop()

try:
    logger.info("Starting main loop...")
    loop.run_until_complete(main(bot))

except KeyboardInterrupt:
    logger.info("Received keyboard interrupt, shutting down...")
    loop.run_until_complete(bot.close())
    # this sleep prevents a bugged exception on Windows
    loop.run_until_complete(asyncio.sleep(1))
    loop.close()
    logger.info("Shutdown complete")

except Exception as e:
    logger.error(f"Fatal error: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)
