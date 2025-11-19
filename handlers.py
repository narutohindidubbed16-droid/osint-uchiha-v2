# HANDLERS.PY — FINAL, CLEAN, RUN-READY
# Features:
# - /start with subscription screen (3 buttons shown; only MAIN+BACKUP verified)
# - Verify join button uses popup (show_alert) and then shows full welcome (photo + main menu)
# - Lookup flow with mode selection, input validation, credits deduction
# - Searching animation: sends video (if available) + searching text
# - Robust API URL builder (supports APIs that use {query} or simple concatenation)
# - Admin helpers (commands: /admin, /addcredits, /removecredits, /userslist) — check MAIN to register in main.py
# - Uses database.py, keyboards.py, utils.py, config.py (as provided earlier)
# - Defensive error handling and logging

print("HANDLERS.PY loaded — final clean version")

import aiohttp
import logging
import re
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from config import (
    MAIN_CHANNEL,
    BACKUP_CHANNEL,
    MOBILE_API,
    GST_API,
    IFSC_API,
    PINCODE_API,
    RC_API,
    IMEI_API,
    ADMIN_ID
)

from keyboards import (
    join_channels_kb,
    main_menu_kb,
    lookup_options_kb,
    ask_input_kb,
    quick_back_kb,
    referral_menu_kb,
    balance_menu_kb,
    buy_credits_kb
)

from database import (
    create_user,
    get_user_credits,
    decrease_credit,
    add_referral,
    admin_add_credits,
    admin_remove_credits,
    get_all_users
)

from utils import validate_input, clean_json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# FIX & NORMALIZE CHANNELS
def fix_channel(ch):
    if not ch:
        return None
    ch = str(ch).strip()
    ch = ch.replace("https://t.me/", "").replace("@", "")
    return ch

MAIN_CH = MAIN_CHANNEL
BACK_CH = BACKUP_CHANNEL

# REAL JOIN CHECK

async def is_joined_all(bot, user_id: int) -> bool:
    try:
        # ALWAYS use @username (never strip it)
        main = await bot.get_chat_member(f"@{MAIN_CH}", user_id)
        back = await bot.get_chat_member(f"@{BACK_CH}", user_id)

        return main.status in ("member", "administrator", "creator") and \
               back.status in ("member", "administrator", "creator")

    except Exception as e:
        logger.warning(f"[JOIN CHECK FAIL] {e}")
        return False
        
def build_api_url(api_template: str, query: str) -> str:
    """
    Build API URL robustly.
    - If api_template contains '{query}', replace it.
    - Else append query intelligently.
    """
    if not api_template:
        return ""
    if "{query}" in api_template:
        return api_template.replace("{query}", query)
    # If API ends with / or ? or =, do not add extra slash
    if api_template.endswith("/") or api_template.endswith("?") or api_template.endswith("="):
        return f"{api_template}{query}"
    # If there is a trailing parameter-like char at end, just concat
    return f"{api_template}{query}"


# ---------------------------
# Subscription / Start screens
# ---------------------------

SUBS_TEXT = (
    "┌────────────────────────────────┐\n"
    "│      🔒  SUBSCRIPTION REQUIRED      │\n"
    "└────────────────────────────────┘\n\n"
    "📢 CHANNEL SUBSCRIPTION REQUIRED\n\n"
    "To access *OSINT Uchiha Bot* you must join our official channels:\n\n"
    "• Updates — @UpdateBotZNagi\n"
    "• BotHub — @AbdulBotZ\n\n"
    "👉 Steps:\n"
    "1️⃣ Join all channels using the buttons below\n"
    "2️⃣ Tap *I HAVE JOINED ALL CHANNELS*\n"
    "3️⃣ Start using the bot\n"
)

WELCOME_IMAGE = "https://i.ibb.co/xGGxX99/uchiha-welcome.jpg"
WELCOME_TEXT = (
    "🔥 *OSINT Uchiha — Dark Intel Clan* 🔥\n\n"
    "👁️ *Mangekyo Multi-Scan Engine Activated*\n\n"
    "⚡ Mobile OSINT\n"
    "⚡ GST Lookup\n"
    "⚡ IFSC / Bank Info\n"
    "⚡ Pincode / Address\n"
    "⚡ Vehicle Details\n"
    "⚡ IMEI Tracking\n\n"
    "Welcome to the most powerful dark-intel engine."
)


async def show_welcome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Send the full welcome screen with image + main menu."""
    chat_id = update.effective_chat.id
    try:
        await ctx.bot.send_photo(
            chat_id=chat_id,
            photo=WELCOME_IMAGE,
            caption=WELCOME_TEXT,
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"[show_welcome] failed to send image: {e}")
        # fallback to text
        await ctx.bot.send_message(
            chat_id=chat_id,
            text=WELCOME_TEXT,
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    /start handler:
    - registers new user in DB (create_user)
    - supports referral codes via /start <referrer_id>
    - if not joined, shows subscription screen (join buttons)
    - if joined, shows welcome
    """
    user = update.effective_user
    args = ctx.args

    # Referral handling (if present and numeric)
    ref = int(args[0]) if (args and args[0].isdigit()) else None

    created = create_user(user.id, user.username, user.first_name)
    if created and ref and ref != user.id:
        add_referral(ref, user.id)
        # notify referrer (best-effort)
        try:
            await ctx.bot.send_message(ref, "🎉 *New Referral — +1 Credit!*", parse_mode="Markdown")
        except Exception:
            pass

    # Check join
    joined = await is_joined_all(ctx.bot, user.id)
    if not joined:
        # Show subscription screen with join buttons (includes private invite link as button)
        await update.message.reply_text(SUBS_TEXT, reply_markup=join_channels_kb(), parse_mode="Markdown")
        return

    # Already joined — show welcome
    await show_welcome(update, ctx)


# ---------------------------
# Verify join (callback)
# ---------------------------
async def verify_join(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Callback when user taps "I HAVE JOINED ALL CHANNELS".
    Uses q.answer with show_alert to give popup feedback.
    If verified — delete the subscription message and send welcome.
    """
    q = update.callback_query
    user_id = q.from_user.id

    # Do not forget to answer callback quickly (to remove spinner)
    # We'll answer with alert messages depending on verification
    joined = await is_joined_all(ctx.bot, user_id)
    if not joined:
        # show_alert True -> popup (modal)
        await q.answer("❌ You must join ALL required channels first!", show_alert=True)
        return

    await q.answer("✅ Verified successfully!", show_alert=True)

    # delete old message (subscription message)
    try:
        await q.message.delete()
    except Exception:
        pass

    # send the full welcome
    await show_welcome(update, ctx)


# ---------------------------
# BUTTONS / Callback handler
# ---------------------------
async def buttons(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Central callback query handler for buttons from keyboards.py
    Important: We respond with new messages (not editing) so each user action creates personal message.
    """
    q = update.callback_query
    data = q.data or ""
    user_id = q.from_user.id

    # Always answer callback to remove "loading" state
    # For some actions we may want to show popup — handle inside functions
    await q.answer()

    # verify join popup handled separately
    if data == "verify_join":
        return await verify_join(update, ctx)

    # Lookup options
    if data == "lookup_options":
        return await ctx.bot.send_message(user_id, "🔍 Select Lookup Type:", reply_markup=lookup_options_kb(), parse_mode="Markdown")

    # Main menu actions: my_balance, referral_menu, buy_credits etc.
    if data == "my_balance":
        credits = get_user_credits(user_id)
        text = f"💳 Your balance: *{credits}* credits\n\nUse *Buy Credits* to top up."
        return await ctx.bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=balance_menu_kb())

    if data == "referral_menu":
        # build referral link
        ref_link = f"https://t.me/{fix_channel(MAIN_CHANNEL)}?start={user_id}"
        return await ctx.bot.send_message(user_id, "Share your referral link to earn +1 credit per sign-up:", reply_markup=referral_menu_kb(ref_link))

    if data == "buy_credits":
        return await ctx.bot.send_message(user_id, "Buy credits panel:", reply_markup=buy_credits_kb())

    if data == "support":
        return await ctx.bot.send_message(user_id, "🛠 Support: @AbdulBotZ", reply_markup=quick_back_kb(), parse_mode="Markdown")

    if data == "help_guide":
        help_text = (
            "📘 *HELP GUIDE*\n\n"
            "`9876543210` → Mobile Lookup\n"
            "`09AAYF1234N1Z2` → GST Lookup\n"
            "`ICIC0001206` → IFSC Lookup\n"
            "`110001` → Pincode Lookup\n"
            "`MH12DE1433` → Vehicle RC\n"
            "`123456789012345` → IMEI Lookup\n"
        )
        return await ctx.bot.send_message(user_id, help_text, reply_markup=quick_back_kb(), parse_mode="Markdown")

    # If selecting a lookup mode
    lookup_map = {
        "mobile_lookup": "📱 Enter Mobile Number (10 digits):",
        "gst_lookup": "🏢 Enter GSTIN (15 chars):",
        "ifsc_lookup": "🏦 Enter IFSC Code (11 chars):",
        "pincode_lookup": "📮 Enter 6-digit Pincode:",
        "vehicle_lookup": "🚗 Enter RC Number (e.g., MH12DE1433):",
        "imei_lookup": "🧾 Enter 15-digit IMEI:"
    }

    if data in lookup_map:
        ctx.user_data["mode"] = data
        return await ctx.bot.send_message(user_id, lookup_map[data], reply_markup=ask_input_kb(), parse_mode="Markdown")

    if data == "back_home":
        return await ctx.bot.send_message(user_id, "🏠 Main Menu:", reply_markup=main_menu_kb(), parse_mode="Markdown")

    # Buy credits quick buttons (example callbacks)
    if data.startswith("buy_"):
        # we keep payments manual — send instruction to pay & confirm
        return await ctx.bot.send_message(user_id, "To buy credits: send payment proof to @LoserNagi and use the correct package button.", reply_markup=buy_credits_kb())


# ---------------------------
# Process user text (lookup)
# ---------------------------
async def process_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Handles free-text messages for lookup queries.
    Flow:
    - Ensure user joined channels
    - Ensure mode is set in ctx.user_data
    - Validate input format using utils.validate_input
    - Deduct credit, send searching video/text, call API, return results
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    # join check
    if not await is_joined_all(ctx.bot, user.id):
        return await update.message.reply_text("❌ You must join all channels first.", reply_markup=join_channels_kb(), parse_mode="Markdown")

    # ensure lookup mode selected
    if "mode" not in ctx.user_data:
        return await update.message.reply_text("⚠️ Please select a lookup from the main menu.", reply_markup=main_menu_kb(), parse_mode="Markdown")

    mode = ctx.user_data["mode"]
    lookup_name = mode.replace("_lookup", "")

    # validate format
    if not validate_input(lookup_name, text):
        return await update.message.reply_text(f"❌ Invalid {lookup_name.upper()} format!", reply_markup=ask_input_kb(), parse_mode="Markdown")

    # credits check
    credits = get_user_credits(user.id)
    if credits <= 0:
        return await update.message.reply_text("❌ You have 0 credits! Buy credits → @LoserNagi", parse_mode="Markdown")

    # deduct credit
    decrease_credit(user.id)

    # send searching animation/message (video preferred)
    SEARCHING_TEXT = (
        "⟢ *OSINT UCHIHA — Searching… Please Wait* ⟣\n"
        ">> *Initializing Uchiha Scan Engine…*\n"
        ">> *Data Streams Activating…*"
    )
    VIDEO_ID = "BAACAgUAAxkBAAICsWkdvOhpHpVHVcRxZQpZAbeZ5jxNAAJxGQACWm3wVPTz0b2H6G8lNgQ"

    try:
        await ctx.bot.send_video(chat_id=chat_id, video=VIDEO_ID, caption=SEARCHING_TEXT, parse_mode="Markdown")
    except Exception as e:
        logger.info(f"[process_text] video send failed: {e}, falling back to text.")
        await ctx.bot.send_message(chat_id=chat_id, text=SEARCHING_TEXT, parse_mode="Markdown")

    # build API url
    api_map = {
        "mobile_lookup": MOBILE_API,
        "gst_lookup": GST_API,
        "ifsc_lookup": IFSC_API,
        "pincode_lookup": PINCODE_API,
        "vehicle_lookup": RC_API,
        "imei_lookup": IMEI_API
    }

    api_template = api_map.get(mode)
    if not api_template:
        await ctx.bot.send_message(chat_id=chat_id, text="⚠️ API not configured for this lookup.", parse_mode="Markdown")
        del ctx.user_data["mode"]
        return

    url = build_api_url(api_template, text)

    # call API
    data = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    logger.warning(f"[process_text] API returned {resp.status} for URL: {url}")
                    await ctx.bot.send_message(chat_id=chat_id, text="⚠️ API Error — please try later.", parse_mode="Markdown")
                    del ctx.user_data["mode"]
                    return
                # try to parse JSON
                try:
                    data = await resp.json()
                except Exception:
                    # maybe API returns plain text — fetch text
                    txt = await resp.text()
                    data = {"raw": txt}
    except Exception as e:
        logger.error(f"[process_text] API call failed: {e}")
        await ctx.bot.send_message(chat_id=chat_id, text="⚠️ API Timeout / Network Error.", parse_mode="Markdown")
        del ctx.user_data["mode"]
        return

    # format and send result
    formatted = clean_json(data)
    result_text = (
        "📄 *OSINT Result*\n\n"
        f"```json\n{formatted}\n```\n"
        f"💳 Credits Left: *{get_user_credits(user.id)}*"
    )

    await ctx.bot.send_message(chat_id=chat_id, text=result_text, parse_mode="Markdown")

    # clear mode
    if "mode" in ctx.user_data:
        del ctx.user_data["mode"]

# ---------------------------
# DIAGNOSTIC COMMAND
# ---------------------------
from config import MAIN_CHANNEL, BACKUP_CHANNEL

from telegram.constants import ChatMemberStatus

async def diag(update, ctx):
    user = update.effective_user
    chat_id = update.effective_chat.id

    MAIN = MAIN_CH
    BACK = BACK_CH

    text = "🔍 *OSINT UCHIHA — DIAGNOSTIC MODE*\n\n"

    text += f"📌 MAIN_CH: `{MAIN}`\n"
    text += f"📌 BACK_CH: `{BACK}`\n\n"

    # ---- TEST 1: Resolve Channel Info ----
    try:
        
        main_info = await ctx.bot.get_chat(f"{MAIN}")
        text += f"🟢 MAIN RESOLVED → ID: `{main_info.id}`\n"
    except Exception as e:
        text += f"🔴 MAIN FAILED → `{e}`\n"

    try:
        back_info = await ctx.bot.get_chat(BACK)
        text += f"🟢 BACKUP RESOLVED → ID: `{back_info.id}`\n\n"
    except Exception as e:
        text += f"🔴 BACKUP FAILED → `{e}`\n\n"

    # ---- TEST 2: Bot admin in MAIN ----
    try:
        bot_info_main = await ctx.bot.get_chat_member(MAIN, ctx.bot.id)
        text += f"🤖 Bot in MAIN: `{bot_info_main.status}`\n"
    except Exception as e:
        text += f"🔴 Bot MAIN check: `{e}`\n"

    # ---- TEST 3: Bot admin in BACKUP ----
    try:
        bot_info_back = await ctx.bot.get_chat_member(BACK, ctx.bot.id)
        text += f"🤖 Bot in BACKUP: `{bot_info_back.status}`\n\n"
    except Exception as e:
        text += f"🔴 Bot BACKUP check: `{e}`\n\n"

    # ---- TEST 4: YOUR membership ----
    try:
        u1 = await ctx.bot.get_chat_member(MAIN, user.id)
        text += f"👤 You in MAIN: `{u1.status}`\n"
    except Exception as e:
        text += f"🔴 User MAIN check: `{e}`\n"

    try:
        u2 = await ctx.bot.get_chat_member(BACK, user.id)
        text += f"👤 You in BACKUP: `{u2.status}`\n"
    except Exception as e:
        text += f"🔴 User BACKUP check: `{e}`\n"

    await ctx.bot.send_message(chat_id, text, parse_mode="Markdown")
# ---------------------------
# ADMIN COMMANDS (helpers)
# ---------------------------
async def admin_panel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    /admin — shows simple admin panel (only for ADMIN_ID)
    Use /addcredits <user_id> <amount> and /removecredits <user_id> <amount>
    Use /userslist to dump DB
    Note: main.py must register this handler if you want to use it.
    """
    user = update.effective_user
    if int(user.id) != int(ADMIN_ID):
        return await update.message.reply_text("❌ You are not authorized to use admin commands.")

    text = (
        "🛠 *Admin Panel*\n\n"
        "/userslist  → List all users\n"
        "/addcredits <user_id> <amount>  → Add credits\n"
        "/removecredits <user_id> <amount> → Remove credits\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def addcredits_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if int(user.id) != int(ADMIN_ID):
        return await update.message.reply_text("❌ Not authorized.")
    args = ctx.args
    if len(args) < 2 or not args[0].isdigit() or not args[1].isdigit():
        return await update.message.reply_text("Usage: /addcredits <user_id> <amount>")
    uid = int(args[0])
    amt = int(args[1])
    ok = admin_add_credits(uid, amt)
    if ok:
        await update.message.reply_text(f"✅ Added {amt} credits to {uid}")
    else:
        await update.message.reply_text("❌ Failed — user not found.")


async def removecredits_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if int(user.id) != int(ADMIN_ID):
        return await update.message.reply_text("❌ Not authorized.")
    args = ctx.args
    if len(args) < 2 or not args[0].isdigit() or not args[1].isdigit():
        return await update.message.reply_text("Usage: /removecredits <user_id> <amount>")
    uid = int(args[0])
    amt = int(args[1])
    ok = admin_remove_credits(uid, amt)
    if ok:
        await update.message.reply_text(f"✅ Removed {amt} credits from {uid}")
    else:
        await update.message.reply_text("❌ Failed — user not found.")


async def userslist_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if int(user.id) != int(ADMIN_ID):
        return await update.message.reply_text("❌ Not authorized.")
    db = get_all_users()
    # keep payload small — show number of users and sample
    total = len(db.keys())
    sample = []
    for i, (k, v) in enumerate(db.items()):
        sample.append(f"{k}: {v.get('credits',0)}cr")
        if i >= 20:
            break
    text = f"👥 Total users: {total}\nSample:\n" + "\n".join(sample)
    await update.message.reply_text(text)


# ---------------------------
# End of handlers.py
# ---------------------------

# NOTE FOR DEPLOY: Make sure main.py registers admin handlers if you want quick admin usage:
# app.add_handler(CommandHandler("admin", admin_panel))
# app.add_handler(CommandHandler("addcredits", addcredits_cmd))
# app.add_handler(CommandHandler("removecredits", removecredits_cmd))
# app.add_handler(CommandHandler("userslist", userslist_cmd))
#
# Also ensure config.py has MAIN_CHANNEL and BACKUP_CHANNEL as usernames (with or without @ is fine).
# The bot must be an admin in those channels to read get_chat_member reliably.
#
# If you still see "old code running" after deploying:
# - Ensure you pushed the changed file and the deploy service used the latest commit
# - Clear any build caches and restart the service
# - Revoke old bot token if you suspect another instance is running with the same token
#
# Good luck — paste this file into repo as handlers.py, update main.py to register admin commands if needed,
# and redeploy. If you want, send me main.py and keyboards.py and I'll produce the exact modified main.py that registers admin handlers.
