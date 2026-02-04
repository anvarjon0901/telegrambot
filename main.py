"""
Stars Shop Bot - Main Entry Point
Professional Version - 100% Working - COMPLETE
"""
import logging
import sys
import time
from datetime import datetime
from telebot import TeleBot

# Setup logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Start the bot"""
    
    print("=" * 60)
    print("🌟 STARS SHOP BOT - PROFESSIONAL VERSION")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    try:
        # Import after logging setup
        from config import Config
        from database import init_db
        from handlers.admin_handlers import register_admin_handlers
        from handlers.user_handlers import register_user_handlers
        
        print(f"👨‍💼 Admin ID: {Config.ADMIN_ID}")
        print(f"💳 Card: {Config.CARD_NUMBER}")
        print("=" * 60)
        
        # Validate config
        Config.validate()
        logger.info("✅ Configuration validated")
        
        # Initialize database
        init_db()
        logger.info("✅ Database initialized")
        
        # Create bot
        bot = TeleBot(Config.BOT_TOKEN, parse_mode=None)
        logger.info("✅ Bot created")
        
        # Register handlers
        register_admin_handlers(bot)
        logger.info("✅ Admin handlers registered")
        
        register_user_handlers(bot)
        logger.info("✅ User handlers registered")
        
        # Test bot connection
        bot_info = bot.get_me()
        logger.info(f"✅ Bot ready: @{bot_info.username}")
        
        print("=" * 60)
        print(f"🤖 Bot polling started: @{bot_info.username}")
        print("⏸️  Stop with: Ctrl+C")
        print("=" * 60)
        
        # Start polling with error handling
        while True:
            try:
                bot.infinity_polling(timeout=60, long_polling_timeout=60)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Polling error: {e}")
                print(f"⚠️ Error: {e}")
                print("♻️ Reconnecting in 5 seconds...")
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("⏹️  Bot stopped")
        print("=" * 60)
        logger.info("Bot stopped (KeyboardInterrupt)")
    
    except Exception as e:
        logger.error(f"❌ Critical error: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}")
        print("♻️ Restarting in 5 seconds...")
        time.sleep(5)
        main()  # Restart


if __name__ == "__main__":
    main()
