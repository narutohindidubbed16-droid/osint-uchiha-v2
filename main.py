print("MAIN FILE — FINAL VERSION")

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

# -----------------------------
# Keep Alive (Render fix)
# -----------------------------
try:
    from keep_alive import keep_alive
except:
    print("ERROR: keep_alive.py missing!")
    sys.exit(1)


# -----------------------------
# IMPORT HANDLERS
# -----------------------------
from handlers import (
    start,
    buttons,
    verify_join,
    process_text,
    admin_panel,
    addcredits_cmd,
    removecredits_cmd,
    userslist_cmd
)


# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")


# -----------------------------
# BOT FUNCTION
# -----------------------------
async def run_bot():

    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN missing!")
        os._exit(1)

    logger.info("🚀 Initializing bot...")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # -----------------------------
    # REGISTER COMMAND HANDLERS
    # -----------------------------
    app.add_handler(CommandHandler("start", start))

    # ADMIN COMMANDS
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("addcredits", addcredits_cmd))
    app.add_handler(CommandHandler("removecredits", removecredits_cmd))
    app.add_handler(CommandHandler("userslist", userslist_cmd))

    # CALLBACK BUTTONS
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))

    # TEXT LOOKUP HANDLER
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, process_text)
    )

    # -----------------------------
    # START BOT
    # -----------------------------
    try:
        await app.initialize()
        await app.start()

        await app.updater.start_polling()
        logger.info("✅ BOT IS LIVE & POLLING…")

        await asyncio.Future()   # Keep running forever

    except Exception as e:
        logger.error(f"❌ BOT ERROR: {e}")

    finally:
        if app.running:
            await app.stop()
        logger.info("Bot stopped.")


# -----------------------------
# MAIN ENTRY POINT
# -----------------------------
if __name__ == "__main__":

    nest_asyncio.apply()
    keep_alive()

    try:
        asyncio.run(run_bot())
    except Exception as e:
        print(f"FATAL ERROR: {e}")
