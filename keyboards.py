from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import MAIN_CHANNEL, BACKUP_CHANNEL

# --------------------------------
# CHANNEL JOIN KEYBOARD
# --------------------------------
def join_channels_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 JOIN DARK NAGI", url="https://t.me/+hyVTTQkfJS41NTFl")],
        [InlineKeyboardButton("📢 JOIN BACKUP", url=f"https://t.me/{BACKUP_CHANNEL.replace('@','')}")],
        [InlineKeyboardButton("📢 JOIN AbdulBotz", url=f"https://t.me/{MAIN_CHANNEL.replace('@','')}")],
        [InlineKeyboardButton("✅ I HAVE JOINED ALL CHANNELS", callback_data="verify_join")]
    ])


# --------------------------------
# MAIN MENU (UPGRADED)
# --------------------------------
def main_menu_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔎 LOOKUPS", callback_data="lookup_options"),
            InlineKeyboardButton("💳 MY BALANCE", callback_data="my_balance")
        ],
        [
            InlineKeyboardButton("👥 EARN CREDITS", callback_data="referral_menu"),
            InlineKeyboardButton("💰 BUY CREDITS", callback_data="buy_credits")
        ],
        [
            InlineKeyboardButton("📚 HELP", callback_data="help_guide"),
            InlineKeyboardButton("🛠 SUPPORT", callback_data="support")
        ]
    ])


# --------------------------------
# REFERRAL MENU
# --------------------------------
def referral_menu_kb(ref_link):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 COPY REFERRAL LINK", url=ref_link)],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# --------------------------------
# BALANCE MENU
# --------------------------------
def balance_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 BUY CREDITS", callback_data="buy_credits")],
        [InlineKeyboardButton("👥 EARN CREDITS", callback_data="referral_menu")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# --------------------------------
# BUY CREDITS PANEL
# --------------------------------
def buy_credits_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("₹49 = 25 Credits", callback_data="buy_25")],
        [InlineKeyboardButton("₹99 = 60 Credits", callback_data="buy_60")],
        [InlineKeyboardButton("₹199 = 150 Credits", callback_data="buy_150")],
        [InlineKeyboardButton("📩 Pay & Send Screenshot", url="https://t.me/LoserNagi")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# --------------------------------
# LOOKUP OPTIONS
# --------------------------------
def lookup_options_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 MOBILE", callback_data="mobile_lookup"),
            InlineKeyboardButton("🏢 GST", callback_data="gst_lookup"),
        ],
        [
            InlineKeyboardButton("🏦 IFSC", callback_data="ifsc_lookup"),
            InlineKeyboardButton("📮 PINCODE", callback_data="pincode_lookup"),
        ],
        [
            InlineKeyboardButton("🚗 VEHICLE", callback_data="vehicle_lookup"),
            InlineKeyboardButton("🧾 IMEI", callback_data="imei_lookup") 
        ],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# --------------------------------
# QUICK SEARCH BACK
# --------------------------------
def quick_back_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 TRY NOW", callback_data="lookup_options")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_home")]
    ])


# --------------------------------
# INPUT BUTTON
# --------------------------------
def ask_input_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 BACK", callback_data="lookup_options")]
    ])
