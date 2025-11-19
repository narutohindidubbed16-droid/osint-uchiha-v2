from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import MAIN_CHANNEL, BACKUP_CHANNEL, PRIVATE_CHANNEL

# --------------------------------
# CHANNEL JOIN KEYBOARD
# --------------------------------
def join_channels_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝙅𝙊𝙄𝙉 𝘿𝘼𝙍𝙆 𝙉𝘼𝙂𝙄", url=f"https://t.me/{PRIVATE_CHANNEL}")],
        [InlineKeyboardButton("📢 𝙅𝙊𝙄𝙉 𝘽𝘼𝘾𝙆𝙐𝙋", url=f"https://t.me/{BACKUP_CHANNEL}")],
        [InlineKeyboardButton("📢 𝙅𝙊𝙄𝙉 𝘼𝙗𝙙𝙪𝙡𝘽𝙤𝙩𝙯", url=f"https://t.me/{MAIN_CHANNEL}")],
        [InlineKeyboardButton("✅ 𝙄 𝙃𝘼𝙑𝙀 𝙅𝙊𝙄𝙉𝙀𝘿 𝘼𝙇𝙇 𝘾𝙃𝘼𝙉𝙉𝙀𝙇𝙎", callback_data="verify_join")]
    ])

# --------------------------------
# MAIN MENU
# --------------------------------
def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔎 LOOKUP OPTIONS", callback_data="lookup_options")],
        [
            InlineKeyboardButton("📚 HELP GUIDE", callback_data="help_guide"),
            InlineKeyboardButton("🛠 SUPPORT", callback_data="support")
        ],
        [InlineKeyboardButton("🚀 QUICK SEARCH", callback_data="quick_search")]
    ])

# --------------------------------
# LOOKUP OPTIONS
# --------------------------------
def lookup_options_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 MOBILE LOOKUP", callback_data="mobile_lookup"),
            InlineKeyboardButton("🏢 GST LOOKUP", callback_data="gst_lookup"),
        ],
        [
            InlineKeyboardButton("🏦 BANK IFSC", callback_data="ifsc_lookup"),
            InlineKeyboardButton("📮 PINCODE", callback_data="pincode_lookup"),
        ],
        [
            InlineKeyboardButton("🚗 VEHICLE LOOKUP", callback_data="vehicle_lookup"),
            InlineKeyboardButton("🧾 IMEI LOOKUP", callback_data="imei_lookup") 
        ],
        [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="back_home")]
    ])

# --------------------------------
# QUICK SEARCH BACK BUTTON
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
