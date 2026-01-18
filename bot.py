from pyrogram import Client
from pyrogram.errors import ApiIdInvalid, AccessTokenInvalid, AccessTokenExpired
from config import API_ID, API_HASH, BOT_TOKEN
import logging
import sys

# Import pyromod with error handling
try:
    from pyromod import listen
    PYROMOD_AVAILABLE = True
except ImportError:
    PYROMOD_AVAILABLE = False
    logger.warning("⚠️  pyromod not available, some features may not work")

# ========================================
# LOGGING CONFIGURATION
# ========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Disable pyrogram's internal logging for cleaner output
logging.getLogger("pyrogram").setLevel(logging.WARNING)

class Bot(Client):
    def __init__(self):
        try:
            super().__init__(
                name="vj_join_request_bot",  # Fixed: Removed spaces (spaces can cause issues)
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                plugins=dict(root="plugins"),
                workers=50,
                sleep_threshold=10
            )
            
            # Initialize pyromod listeners if available
            if PYROMOD_AVAILABLE:
                try:
                    self.listeners = {}
                    logger.info("✅ Pyromod listeners initialized")
                except Exception as e:
                    logger.warning(f"⚠️  Could not initialize pyromod: {e}")
            
            logger.info("✅ Bot instance created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create bot instance: {e}")
            sys.exit(1)
      
    async def start(self):
        try:
            logger.info("🔄 Starting bot...")
            await super().start()
            
            # Get bot information
            me = await self.get_me()
            self.username = '@' + me.username
            
            # Success message with bot details
            logger.info("="*60)
            logger.info("🎉 BOT STARTED SUCCESSFULLY!")
            logger.info("="*60)
            logger.info(f"📱 Bot Name: {me.first_name}")
            logger.info(f"🆔 Bot Username: {self.username}")
            logger.info(f"🔢 Bot ID: {me.id}")
            logger.info(f"✅ Bot is now online and ready to accept commands")
            logger.info("="*60)
            logger.info("💡 Powered By @VJ_Botz")
            logger.info("="*60)
            
        except ApiIdInvalid:
            logger.error("❌ ERROR: API_ID is invalid!")
            logger.error("   Please check your API_ID from https://my.telegram.org")
            sys.exit(1)
            
        except AccessTokenInvalid:
            logger.error("❌ ERROR: BOT_TOKEN is invalid!")
            logger.error("   Please get a new token from @BotFather")
            logger.error("   Steps: /newbot or /token")
            sys.exit(1)
            
        except AccessTokenExpired:
            logger.error("❌ ERROR: BOT_TOKEN has expired!")
            logger.error("   Please regenerate token from @BotFather")
            sys.exit(1)
            
        except Exception as e:
            logger.error(f"❌ ERROR: Failed to start bot!")
            logger.error(f"   Error details: {str(e)}")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error("\n💡 Common fixes:")
            logger.error("   1. Check all environment variables are set correctly")
            logger.error("   2. Verify BOT_TOKEN is valid (test at https://api.telegram.org/bot<TOKEN>/getMe)")
            logger.error("   3. Check API_ID and API_HASH from https://my.telegram.org")
            logger.error("   4. Ensure internet connection is stable")
            sys.exit(1)

    async def stop(self, *args):
        try:
            logger.info("🔄 Stopping bot...")
            await super().stop()
            logger.info("="*60)
            logger.info("👋 Bot Stopped Successfully")
            logger.info("   Thank you for using VJ Join Request Bot")
            logger.info("="*60)
        except Exception as e:
            logger.error(f"⚠️  Error while stopping bot: {e}")

# ========================================
# RUN BOT
# ========================================
if __name__ == "__main__":
    try:
        logger.info("🚀 Initializing VJ Join Request Bot...")
        logger.info("="*60)
        
        bot = Bot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Bot stopped by user (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}")
        logger.error("   Bot cannot start. Please check configuration.")
        sys.exit(1)
