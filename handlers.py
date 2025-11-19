print("HANDLERS UPDATED v2 — PART 1")

import aiohttp
import logging
from telegram import Update
from telegram.ext import ContextTypes

# CONFIG IMPORT (username variables without @ fix)
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

UCHIHA_VIDEO = "BAACAgUAAxkBAAICsWkdvOhpHpVHVcRxZQpZAbeZ5jxNAAJxGQACWm3wVPTz0b2H6G8lNgQ"


# ============================
#  CLEAN CHANNEL USERNAMES
# ============================
def fix_channel(ch):
    if not ch:
        return None
    ch = ch.replace("https://t.me/", "")
    ch = ch.replace("@", "")
    return ch


MAIN_CH = fix_channel(MAIN_CHANNEL)
BACK_CH = fix_channel(BACKUP_CHANNEL)


# ============================
#  JOIN CHECK (FIXED)
# ============================
async def is_joined_all(bot, user_id):
    try:
        status_ok = ("member", "administrator", "creator")

        c1 = await bot.get_chat_member(BACK_CH, user_id)
        c2 = await bot.get_chat_member(MAIN_CH, user_id)

        return (c1.status in status_ok and c2.status in status_ok)

    except Exception as e:
        logger.error(f"[JOIN CHECK ERROR] {e}")
        return False


# ============================
#  START — SUBSCRIBE FIRST SCREEN
# ============================
SUBS_TEXT = """
┌────────────────────────────────┐
│      🔒 𝙎𝙐𝘽𝙎𝘾𝙍𝙄𝙋𝙏𝙄𝙊𝙉 𝙍𝙀𝙌𝙐𝙄𝙍𝙀𝘿      │
└────────────────────────────────┘

📢 𝘾𝙃𝘼𝙉𝙉𝙀𝙇 𝙎𝙐𝘽𝙎𝘾𝙍𝙄𝙋𝙏𝙄𝙊𝙉 𝙍𝙀𝙌𝙐𝙄𝙍𝙀𝘿

𝙏𝙤 𝙖𝙘𝙘𝙚𝙨𝙨 **OSINT Uchiha Bot**, you must join our channels:

• **Updates:** @UpdateBotZNagi  
• **BotHub:** @AbdulBotZ  

👉 𝐒𝐭𝐞𝐩𝐬  
1️⃣ Join all channels  
2️⃣ Click **I HAVE JOINED ALL CHANNELS**  
3️⃣ Start using bot
"""


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    args = ctx.args

    # New user auto credit + referral
    ref = int(args[0]) if (args and args[0].isdigit()) else None
    created = create_user(user.id, user.username, user.first_name)

    if created and ref and ref != user.id:
        add_referral(ref, user.id)
        try:
            await ctx.bot.send_message(ref, "🎉 *New Referral — +1 Credit!*", parse_mode="Markdown")
        except:
            pass

    # If not joined → show subscription screen
    if not await is_joined_all(ctx.bot, user.id):
        await update.message.reply_text(
            SUBS_TEXT,
            reply_markup=join_channels_kb()
        )
        return

    # If joined → show real welcome screen (next part)
    await show_welcome(update, ctx)# ============================
#   REAL WELCOME SCREEN
# ============================
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

Welcome to the most powerful dark-intel bot on Telegram.
"""


async def show_welcome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """When user verified join, show full welcome screen."""

    chat_id = update.effective_chat.id

    await ctx.bot.send_photo(
        chat_id=chat_id,
        photo=WELCOME_IMAGE,
        caption=WELCOME_TEXT,
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )


# ============================
#   VERIFY JOIN BUTTON (POPUP)
# ============================
async def verify_join(update, ctx):
    q = update.callback_query

    joined = await is_joined_all(ctx.bot, q.from_user.id)

    if not joined:
        # POPUP (alert=True)
        await q.answer("❌ You must join ALL required channels first!", show_alert=True)
        return

    # POPUP success
    await q.answer("✅ Verified successfully!", show_alert=True)

    # Delete old subscription message
    try:
        await q.message.delete()
    except:
        pass

    # Show full welcome screen
    await show_welcome(update, ctx)


# ============================
#   BUTTON HANDLER
# ============================
async def buttons(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    data = q.data

    # We always answer callback to remove loading animation
    await q.answer()

    # JOIN VERIFICATION
    if data == "verify_join":
        await verify_join(update, ctx)
        return

    # LOOKUP OPTIONS
    if data == "lookup_options":
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text="🔍 Select Lookup Type:",
            reply_markup=lookup_options_kb(),
            parse_mode="Markdown"
        )
        return

    # HELP
    if data == "help_guide":
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text=(
                "📘 *HELP GUIDE*\n\n"
                "`9876543210` → Mobile Lookup\n"
                "`09AAYF1234N1Z2` → GST Lookup\n"
                "`ICIC0001206` → IFSC Lookup\n"
                "`110001` → Pincode Lookup\n"
                "`MH12DE1433` → Vehicle RC\n"
                "`123456789012345` → IMEI Lookup"
            ),
            reply_markup=quick_back_kb(),
            parse_mode="Markdown"
        )
        return

    # SUPPORT
    if data == "support":
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text="🛠 Support: @AbdulBotZ",
            reply_markup=quick_back_kb(),
            parse_mode="Markdown"
        )
        return

    # SELECT LOOKUP MODE
    lookup_msg = {
        "mobile_lookup": "📱 Send 10-digit Mobile Number:",
        "gst_lookup": "🏢 Send 15-digit GSTIN:",
        "ifsc_lookup": "🏦 Send Bank IFSC Code:",
        "pincode_lookup": "📮 Send 6-Digit Pincode:",
        "vehicle_lookup": "🚗 Send Vehicle Number:",
        "imei_lookup": "🧾 Send 15-Digit IMEI:"
    }

    if data in lookup_msg:
        ctx.user_data["mode"] = data
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text=lookup_msg[data],
            reply_markup=ask_input_kb(),
            parse_mode="Markdown"
        )
        return

    # BACK BUTTON
    if data == "back_home":
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text="🏠 Main Menu:",
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )
        # ============================
# PROCESS LOOKUP INPUT
# ============================
async def process_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    msg = update.message.text.strip()

    # CHECK JOIN
    if not await is_joined_all(ctx.bot, user.id):
        await update.message.reply_text(
            "❌ *You must join all channels first!*",
            reply_markup=join_channels_kb(),
            parse_mode="Markdown"
        )
        return

    # CHECK lookup mode
    if "mode" not in ctx.user_data:
        await update.message.reply_text(
            "⚠️ Select lookup from main menu.",
            reply_markup=main_menu_kb()
        )
        return

    mode = ctx.user_data["mode"]
    lookup_name = mode.replace("_lookup", "")

    # INPUT VALIDATION
    if not validate_input(lookup_name, msg):
        await update.message.reply_text(
            f"❌ Invalid *{lookup_name.upper()}* format!",
            reply_markup=ask_input_kb(),
            parse_mode="Markdown"
        )
        return

    # CHECK CREDITS
    credits = get_user_credits(user.id)
    if credits <= 0:
        await update.message.reply_text(
            "❌ *You have 0 Credits!*\nBuy Credits → @LoserNagi",
            parse_mode="Markdown"
        )
        return

    # DEDUCT CREDIT
    decrease_credit(user.id)

    # ============================
    # SEND SEARCHING VIDEO + TEXT
    # ============================
    UCHIHA_VIDEO = "BAACAgUAAxkBAAICsWkdvOhpHpVHVcRxZQpZAbeZ5jxNAAJxGQACWm3wVPTz0b2H6G8lNgQ"

    SEARCHING_TEXT = (
        "⟢ *OSINT UCHIHA — Searching… Please Wait* ⟣\n"
        ">> *Initializing Uchiha Scan Engine…*\n"
        ">> *Data Streams Activating…*"
    )

    try:
        await ctx.bot.send_video(
            chat_id=chat_id,
            video=UCHIHA_VIDEO,
            caption=SEARCHING_TEXT,
            parse_mode="Markdown"
        )
    except:
        await ctx.bot.send_message(
            chat_id=chat_id,
            text=SEARCHING_TEXT,
            parse_mode="Markdown"
        )

    # ============================
    # API CALL SYSTEM
    # ============================
    api_map = {
        "mobile_lookup": MOBILE_API + msg,
        "gst_lookup": GST_API + msg,
        "ifsc_lookup": IFSC_API + msg,
        "pincode_lookup": PINCODE_API + msg,
        "vehicle_lookup": RC_API + msg,
        "imei_lookup": IMEI_API + msg
    }

    url = api_map.get(mode)
    data = None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                else:
                    await ctx.bot.send_message(
                        chat_id=chat_id,
                        text="⚠️ *API Error — Server Down!*",
                        parse_mode="Markdown"
                    )
                    return

    except Exception as e:
        logger.error(e)
        await ctx.bot.send_message(
            chat_id=chat_id,
            text="⚠️ *API Timeout or Invalid Response!*",
            parse_mode="Markdown"
        )
        return

    # ============================
    # FORMAT RESULT
    # ============================
    formatted = clean_json(data)

    result_text = (
        "📄 **OSINT Result**\n\n"
        f"```json\n{formatted}\n```\n"
        f"💳 Credits Left: *{get_user_credits(user.id)}*\n"
    )

    # SEND RESULT
    await ctx.bot.send_message(
        chat_id=chat_id,
        text=result_text,
        parse_mode="Markdown"
    )

    # CLEAR MODE
    del ctx.user_data["mode"]
