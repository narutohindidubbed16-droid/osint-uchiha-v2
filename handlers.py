print("LOADED NEW HANDLERS v69")
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

UCHIHA_VIDEO = "BAACAgUAAxkBAAICsWkdvOhpHpVHVcRxZQpZAbeZ5jxNAAJxGQACWm3wVPTz0b2H6G8lNgQ"
WELCOME_IMAGE = "https://ibb.co/JFSXQ6Yt"

WELCOME_TEXT = """🔥 **ᴏꜱɪɴᴛ ᴜᴄʜɪʜᴀ — ᴅᴀʀᴋ ɪɴᴛᴇʟ ᴄʟᴀɴ** 🔥

╔═══ ◎ **ᴍᴀɴɢᴇᴋʏᴏ ᴅᴀᴛᴀ ꜱᴄᴀɴ ᴇɴɢɪɴᴇ** ◎
║ ᴅᴇᴇᴘ ᴡᴇʙ • ᴅᴀʀᴋ ᴛʀᴀɪʟꜱ • ʀᴇᴀʟ-ᴛɪᴍᴇ ɪɴᴛᴇʟ
╚═══════════════════════

👁️ **ꜱʜᴀʀɪɴɢᴀɴ ꜰᴇᴀᴛᴜʀᴇ ᴜɴʟᴏᴄᴋᴇᴅ**
⚡ ᴍᴏʙɪʟᴇ ᴅᴀᴛᴀ ᴘᴜʟʟ
⚡ ɢꜱᴛ ʀᴇɢɪꜱᴛʀᴀᴛɪᴏɴ
⚡ ɪꜰꜱᴄ ᴅᴇᴄᴏᴅᴇ
⚡ ᴘɪɴᴄᴏᴅᴇ / ᴘᴏꜱᴛᴀʟ ᴛʀᴀᴄᴇ
⚡ ᴠᴇʜɪᴄʟᴇ ʀᴇᴄᴏʀᴅ ꜱᴄᴀɴ

🔥 **ᴏᴘᴇʀᴀᴛɪɴɢ ɪɴ ᴜᴄʜɪʜᴀ ᴍᴏᴅᴇ…**
ᴏɴᴇ ᴛᴀᴘ → ᴅᴀᴛᴀ ᴜɴʀᴀᴠᴇʟꜱ
ᴏɴᴇ ʟᴏᴏᴋ → ɪɴꜰᴏ ᴇxᴘᴏꜱᴇᴅ
ᴏɴᴇ ᴄᴏᴍᴍᴀɴᴅ → ᴄʟᴀɴ ᴘᴏᴡᴇʀ ᴜɴʟᴇᴀꜱʜᴇᴅ
"""

SEARCHING_TEXT = """
⟢ *OSINT UCHIHA — Searching… Please Wait* ⟣  
>> *Initializing Uchiha Scan Engine…*  
>> *Data Streams Activating…*  
"""

# -------------------------------------------------
# CHECK CHANNELS (MAIN + BACKUP ONLY)
# -------------------------------------------------
async def is_joined_all(bot, user_id):
    try:
        status_ok = ("member", "administrator", "creator")

        # CHECK ONLY BACKUP + MAIN
        c1 = await bot.get_chat_member(BACKUP_CHANNEL, user_id)
        c2 = await bot.get_chat_member(MAIN_CHANNEL, user_id)

        return (
            c1.status in status_ok and
            c2.status in status_ok
        )

    except Exception as e:
        logger.error(f"Join check failed: {e}")
        return False

# -------------------------------------------------
# /START COMMAND
# -------------------------------------------------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = ctx.args

    # Referral
    ref = int(args[0]) if (args and args[0].isdigit()) else None
    created = create_user(user.id, user.username, user.first_name)

    if created and ref and ref != user.id:
        add_referral(ref, user.id)
        try:
            await ctx.bot.send_message(
                chat_id=ref,
                text="🎉 *New Referral! +1 Credit Added*",
                parse_mode="Markdown"
            )
        except:
            pass

    if not await is_joined_all(ctx.bot, user.id):
        await update.message.reply_text(
            "🔐 *Join all channels first:*",
            reply_markup=join_channels_kb(),
            parse_mode="Markdown"
        )
        return

    # SEND WELCOME IMAGE + TEXT
    await ctx.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=WELCOME_IMAGE,
        caption=WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )

# -------------------------------------------------
# VERIFY JOIN
# -------------------------------------------------
async def verify_join(update, ctx):
    q = update.callback_query
    await q.answer()

    if await is_joined_all(ctx.bot, q.from_user.id):
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text="✅ Verified! Access Granted.",
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )
    else:
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text="❌ Please join Backup + AbdulBotz channels first.",
            reply_markup=join_channels_kb()
        )

# -------------------------------------------------
# BUTTON HANDLER (NEW MESSAGE, NOT EDIT)
# -------------------------------------------------
async def buttons(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()

    if data == "lookup_options":
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text="🔍 Select Lookup Type:",
            reply_markup=lookup_options_kb(),
            parse_mode="Markdown"
        )
        return

    if data == "help_guide":
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text=(
                "📘 *HELP GUIDE*\n\n"
                "`9876543210` - Mobile\n"
                "`GST` - GST\n"
                "`IFSC` - Bank\n"
                "`Pincode`\n"
                "`Vehicle`\n"
                "`IMEI`\n"
            ),
            reply_markup=quick_back_kb(),
            parse_mode="Markdown"
        )
        return

    if data == "support":
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text="🛠 Support: @AbdulBotz",
            reply_markup=quick_back_kb(),
            parse_mode="Markdown"
        )
        return

    lookup_modes = {
        "mobile_lookup": "📱 Send Mobile Number:",
        "gst_lookup": "🏢 Send GST Number:",
        "ifsc_lookup": "🏦 Send IFSC:",
        "pincode_lookup": "📮 Send Pincode:",
        "vehicle_lookup": "🚗 Send Vehicle Number:",
        "imei_lookup": "🧾 Send IMEI:"
    }

    if data in lookup_modes:
        ctx.user_data["mode"] = data
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text=lookup_modes[data],
            reply_markup=ask_input_kb(),
            parse_mode="Markdown"
        )
        return

    if data == "back_home":
        await ctx.bot.send_message(
            chat_id=q.from_user.id,
            text="🏠 Main Menu:",
            reply_markup=main_menu_kb(),
            parse_mode="Markdown"
        )

# -------------------------------------------------
# PROCESS USER INPUT (Custom Searching + Video)
# -------------------------------------------------
async def process_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message.text.strip()

    if not await is_joined_all(ctx.bot, user.id):
        await update.message.reply_text(
            "🔐 Join channels first.",
            reply_markup=join_channels_kb()
        )
        return

    if "mode" not in ctx.user_data:
        await update.message.reply_text(
            "Select lookup from menu.",
            reply_markup=main_menu_kb()
        )
        return

    mode = ctx.user_data["mode"]
    lookup_type = mode.replace("_lookup", "")

    if not validate_input(lookup_type, msg):
        await update.message.reply_text(
            f"❌ Invalid {lookup_type.upper()} format!",
            reply_markup=ask_input_kb()
        )
        return

    credits = get_user_credits(user.id)
    if credits <= 0:
        await update.message.reply_text(
            "❌ *No Credits!*",
            parse_mode="Markdown"
        )
        return

    decrease_credit(user.id)

    # NEW: UCHIHA VIDEO + SEARCHING MESSAGE
    await ctx.bot.send_video(
        chat_id=update.effective_chat.id,
        video=UCHIHA_VIDEO,
        caption=SEARCHING_TEXT,
        parse_mode="Markdown"
    )

    # ---------------- API CALL ----------------
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
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=15) as r:
                if r.status == 200:
                    data = await r.json()
                else:
                    await update.message.reply_text(
                        "⚠️ API Error.",
                        parse_mode="Markdown"
                    )
                    return
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("⚠️ API Timeout.")
        return

    formatted_data = clean_json(data)

    result = (
        f"📄 *OSINT Result*\n\n```json\n{formatted_data}\n```\n"
        f"💳 Credits Left: *{get_user_credits(user.id)}*"
    )

    await ctx.bot.send_message(
        chat_id=update.effective_chat.id,
        text=result,
        parse_mode="Markdown"
    )

    del ctx.user_data["mode"]
