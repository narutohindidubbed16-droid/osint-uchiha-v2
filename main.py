print("MAIN FILE UPDATED v69")
import os
import asyncio
import nest_asyncio
import logging
import sys

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# -------- Keep Alive (Render fix) --------
try:
    from keep_alive import keep_alive
except:
    print("ERROR: keep_alive.py missing!")
    sys.exit(1)

# -------- Handlers Import --------
from handlers import (
    start,
    buttons,
    verify_join,
    process_text
)

# -------- Logging --------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def run_bot():

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN missing in environment!")
        os._exit(1)

    logger.info("🔧 Initializing bot...")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # -------- REGISTER HANDLERS --------
    app.add_handler(CommandHandler("start", start))

    # Buttons (callback_query)
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))

    # Text processor
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, process_text)
    )

    # -------- START BOT --------
    try:
        await app.initialize()
        await app.start()

        # Render Fix
        await app.updater.start_polling()

        logger.info("✅ Bot is ONLINE & POLLING.")
        await asyncio.Future()

    except Exception as e:
        logger.error(f"❌ Polling Error: {e}")

    finally:
        if app.running:
            await app.stop()
        logger.info("Bot Stopped!")


if __name__ == "__main__":
    nest_asyncio.apply()
    keep_alive()

    try:
        asyncio.run(run_bot())
    except Exception as e:
        logger.error(f"Fatal Error: {e}")
