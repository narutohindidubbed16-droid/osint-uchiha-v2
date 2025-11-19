print("HANDLERS UPDATED — FINAL CLEAN VERSION")

import aiohttp
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import (
    MAIN_CHANNEL,
    BACKUP_CHANNEL,
    MOBILE_API,
    GST_API,
    IFSC_API,
    PINCODE_API,
    RC_API,
    IMEI_API
)

from keyboards import (
    join_channels_kb,
    main_menu_kb,
    lookup_options_kb,
    ask_input_kb,
    quick_back_kb
)

from database import (
    create_user,
    get_user_credits,
    decrease_credit,
    add_referral
)

from utils import validate_input, clean_json

logger = logging.getLogger(__name__)

# ---------------------------
# FIX CHANNEL USERNAMES
# ---------------------------
def fix_channel(ch):
    if not ch:
        return None
    ch = ch.replace("https://t.me/", "").replace("@", "")
    return ch

MAIN_CH = fix_channel(MAIN_CHANNEL)
BACK_CH = fix_channel(BACKUP_CHANNEL)

# ---------------------------
# JOIN CHECK
# ---------------------------
async def is_joined_all(bot, user_id):
    try:
        statuses = ("member", "administrator", "creator")

        c1 = await bot.get_chat_member(BACK_CH, user_id)
        c2 = await bot.get_chat_member(MAIN_CH, user_id)

        return c1.status in statuses and c2.status in statuses

    except Exception as e:
        logger.error(f"[JOIN CHECK ERROR] {e}")
        return False


# ---------------------------
# SUBSCRIPTION SCREEN
# ---------------------------
SUBS_TEXT = """
┌────────────────────────────────┐
│      🔒 𝙎𝙐𝘽𝙎𝘾𝙍𝙄𝙋𝙏𝙄𝙊𝙉 𝙍𝙀𝙌𝙐𝙄𝙍𝙀𝘿      │
└────────────────────────────────┘

📢 𝘾𝙃𝘼𝙉𝙉𝙀𝙇 𝙎𝙐𝘽𝙎𝘾𝙍𝙄𝙋𝙏𝙄𝙊𝙉 𝙍𝙀𝙌𝙐𝙄𝙍𝙀𝘿

To access **OSINT Uchiha Bot**, join all channels:

• **Updates** — @UpdateBotZNagi  
• **BotHub** — @AbdulBotZ  

👉 Steps  
1️⃣ Join all channels  
2️⃣ Tap **I HAVE JOINED ALL CHANNELS**  
3️⃣ Start using bot
"""

# ---------------------------
# START COMMAND
# ---------------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = ctx.args

    ref = int(args[0]) if (args and args[0].isdigit()) else None
    new_user = create_user(user.id, user.username, user.first_name)

    if new_user and ref and ref != user.id:
        add_referral(ref, user.id)
        try:
            await ctx.bot.send_message(
                ref,
                "🎉 *New Referral — +1 Credit!*",
                parse_mode="Markdown"
            )
        except:
            pass

    if not await is_joined_all(ctx.bot, user.id):
        await update.message.reply_text(
            SUBS_TEXT,
            reply_markup=join_channels_kb()
        )
        return

    await show_welcome(update, ctx)


# ---------------------------
# FULL WELCOME SCREEN
# ---------------------------
WELCOME_IMAGE = "https://i.ibb.co/xGGxX99/uchiha-welcome.jpg"
WELCOME_TEXT = """
🔥 **OSINT Uchiha — Dark Intel Clan** 🔥

👁️ *Mangekyo Multi-Scan Engine Activated*

⚡ Mobile OSINT  
⚡ GST Lookup  
⚡ IFSC / Bank Info  
⚡ Pincode / Address  
⚡ Vehicle Details  
⚡ IMEI Tracking  

Welcome to the most powerful dark-intel engine.
"""

async def show_welcome(update, ctx):
    await ctx.bot.send_photo(
        update.effective_chat.id,
        WELCOME_IMAGE,
        caption=WELCOME_TEXT,
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )


# ---------------------------
# VERIFY JOIN
# ---------------------------
async def verify_join(update, ctx):
    q = update.callback_query
    user_id = q.from_user.id

    joined = await is_joined_all(ctx.bot, user_id)

    if not joined:
        await q.answer("❌ Join ALL required channels!", show_alert=True)
        return

    await q.answer("✅ Verified successfully!", show_alert=True)

    try: await q.message.delete()
    except: pass

    await show_welcome(update, ctx)


# ---------------------------
# BUTTON HANDLER
# ---------------------------
async def buttons(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()

    if data == "verify_join":
        return await verify_join(update, ctx)

    if data == "lookup_options":
        return await ctx.bot.send_message(
            q.from_user.id,
            "🔍 Select Lookup Type:",
            reply_markup=lookup_options_kb(),
            parse_mode="Markdown"
        )

    if data == "help_guide":
        return await ctx.bot.send_message(
            q.from_user.id,
            "📘 *HELP GUIDE*\n"
            "`9876543210` → Mobile\n"
            "`ICIC0001206` → IFSC\n"
            "`09AAYF1234N1Z2` → GST\n"
            "`110001` → Pincode\n"
            "`MH12DE1433` → RC\n"
            "`123456789012345` → IMEI",
            reply_markup=quick_back_kb(),
            parse_mode="Markdown"
        )

    if data == "support":
        return await ctx.bot.send_message(
            q.from_user.id,
            "🛠 Support: @AbdulBotZ",
            reply_markup=quick_back_kb(),
            parse_mode="Markdown"
        )

    lookup_text = {
        "mobile_lookup": "📱 Enter Mobile Number:",
        "gst_lookup": "🏢 Enter GSTIN:",
        "ifsc_lookup": "🏦 Enter IFSC Code:",
        "pincode_lookup": "📮 Enter Pincode:",
        "vehicle_lookup": "🚗 Enter Vehicle Number:",
        "imei_lookup": "🧾 Enter IMEI Number:"
    }

    if data in lookup_text:
        ctx.user_data["mode"] = data
        return await ctx.bot.send_message(
            q.from_user.id,
            lookup_text[data],
            reply_markup=ask_input_kb(),
            parse_mode="Markdown"
        )

    if data == "back_home":
        return await ctx.bot.send_message(
            q.from_user.id,
            "🏠 Main Menu:",
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )


# ---------------------------
# PROCESS TEXT (OSINT SEARCH)
# ---------------------------
async def process_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if not await is_joined_all(ctx.bot, user.id):
        return await update.message.reply_text(
            "❌ Join channels first.",
            reply_markup=join_channels_kb()
        )

    if "mode" not in ctx.user_data:
        return await update.message.reply_text(
            "⚠ Select lookup from menu.",
            reply_markup=main_menu_kb()
        )

    mode = ctx.user_data["mode"]
    lookup_type = mode.replace("_lookup", "")

    if not validate_input(lookup_type, text):
        return await update.message.reply_text(
            f"❌ Invalid {lookup_type.upper()} format!",
            reply_markup=ask_input_kb()
        )

    credits = get_user_credits(user.id)
    if credits <= 0:
        return await update.message.reply_text(
            "❌ *You have 0 credits!*\nBuy credits → @LoserNagi",
            parse_mode="Markdown"
        )

    decrease_credit(user.id)

    # SEARCHING ANIMATION
    SEARCH_TEXT = (
        "⟢ *OSINT UCHIHA — Searching…* ⟣\n"
        ">> Initializing Uchiha Scan Engine…\n"
        ">> Data Streams Activating…"
    )

    VIDEO_ID = "BAACAgUAAxkBAAICsWkdvOhpHpVHVcRxZQpZAbeZ5jxNAAJxGQACWm3wVPTz0b2H6G8lNgQ"

    try:
        await ctx.bot.send_video(chat_id, VIDEO_ID, caption=SEARCH_TEXT, parse_mode="Markdown")
    except:
        await ctx.bot.send_message(chat_id, SEARCH_TEXT, parse_mode="Markdown")

    # API MAP
    api_map = {
        "mobile_lookup": MOBILE_API + text,
        "gst_lookup": GST_API + text,
        "ifsc_lookup": IFSC_API + text,
        "pincode_lookup": PINCODE_API + text,
        "vehicle_lookup": RC_API + text,
        "imei_lookup": IMEI_API + text
    }

    url = api_map[mode]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    return await ctx.bot.send_message(chat_id, "⚠ API Error!", parse_mode="Markdown")
                data = await resp.json()

    except Exception as e:
        logger.error(e)
        return await ctx.bot.send_message(chat_id, "⚠ API Timeout!", parse_mode="Markdown")

    formatted = clean_json(data)

    result = (
        "📄 **OSINT Result**\n\n"
        f"```json\n{formatted}\n```\n"
        f"💳 Credits Left: *{get_user_credits(user.id)}*"
    )

    await ctx.bot.send_message(chat_id, result, parse_mode="Markdown")

    del ctx.user_data["mode"]
