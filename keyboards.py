from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import MAIN_CHANNEL, BACKUP_CHANNEL, PRIVATE_CHANNEL

# ===============================================================
# 🔐 CHANNEL JOIN KEYBOARD  (Private = only button, NO check)
# ===============================================================
def join_channels_kb():
    kb = [
        [InlineKeyboardButton("📢 JOIN MAIN", url=f"https://t.me/{MAIN_CHANNEL.replace('@','')}")],
        [InlineKeyboardButton("📢 JOIN BACKUP", url=f"https://t.me/{BACKUP_CHANNEL.replace('@','')}")],
    ]

    # PRIVATE channel optional (no join check)
    if PRIVATE_CHANNEL and PRIVATE_CHANNEL != "":
        kb.append([InlineKeyboardButton("📢 JOIN PRIVATE", url=f"https://t.me/{PRIVATE_CHANNEL.replace('@','')}")])

    kb.append([InlineKeyboardButton("✅ I HAVE JOINED ALL CHANNELS", callback_data="verify_join")])

    return InlineKeyboardMarkup(kb)
# ===============================================================
# 🏠 MAIN MENU BUTTONS
# ===============================================================
def main_menu_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 START LOOKUP", callback_data="lookup_options"),
            InlineKeyboardButton("💳 MY BALANCE", callback_data="my_balance")
        ],
        [
            InlineKeyboardButton("👥 REFERRAL", callback_data="referral_menu"),
            InlineKeyboardButton("💰 BUY CREDITS", callback_data="buy_credits")
        ],
        [InlineKeyboardButton("📘 HELP GUIDE", callback_data="help_guide")]
    ])

# ===============================================================
# 👥 REFERRAL MENU
# ===============================================================
def referral_menu_kb(ref_link):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 COPY REFERRAL LINK", url=ref_link)],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# ===============================================================
# 💳 BALANCE PANEL
# ===============================================================
def balance_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 BUY CREDITS", callback_data="buy_credits")],
        [InlineKeyboardButton("👥 EARN CREDITS", callback_data="referral_menu")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# ===============================================================
# 💰 BUY CREDITS PANEL
# ===============================================================
def buy_credits_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("₹49 = 25 Credits", callback_data="buy_25")],
        [InlineKeyboardButton("₹99 = 60 Credits", callback_data="buy_60")],
        [InlineKeyboardButton("₹199 = 150 Credits", callback_data="buy_150")],
        [InlineKeyboardButton("📩 Pay & Send Screenshot", url="https://t.me/LoserNagi")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# ===============================================================
# 🔍 LOOKUP OPTIONS
# ===============================================================
def lookup_options_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 MOBILE", callback_data="mobile_lookup"),
            InlineKeyboardButton("🏢 GST", callback_data="gst_lookup")
        ],
        [
            InlineKeyboardButton("🏦 IFSC", callback_data="ifsc_lookup"),
            InlineKeyboardButton("📮 PINCODE", callback_data="pincode_lookup")
        ],
        [
            InlineKeyboardButton("🚗 VEHICLE", callback_data="vehicle_lookup"),
            InlineKeyboardButton("🧾 IMEI", callback_data="imei_lookup")
        ],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# ===============================================================
# 🔙 QUICK SEARCH BACK
# ===============================================================
def quick_back_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 TRY NOW", callback_data="lookup_options")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# ===============================================================
# ✏ ASK INPUT BUTTON
# ===============================================================
def ask_input_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 BACK", callback_data="lookup_options")]
    ])
