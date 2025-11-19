import os

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Channel Usernames/Links (Stored as strings, NO int() conversion)
# Render value should be like: '@MainChannelUsername' or 'https://t.me/MainChannel'
MAIN_CHANNEL = os.getenv("MAIN_CHANNEL")
BACKUP_CHANNEL = os.getenv("BACKUP_CHANNEL")
PRIVATE_CHANNEL = os.getenv("PRIVATE_CHANNEL")

# API URLs (Keep as strings)
MOBILE_API = os.getenv("MOBILE_API")
GST_API = os.getenv("GST_API")
IFSC_API = os.getenv("IFSC_API")
PINCODE_API = os.getenv("PINCODE_API")
VEHICLE_API = os.getenv("VEHICLE_API")
RC_API = os.getenv("VEHICLE_API") 
IMEI_API = os.getenv("IMEI_API") 

# Admin Settings (Keep as integer)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Default starting credits (Keep as integer)
START_CREDITS = int(os.getenv("START_CREDITS", "5"))

# Bot Info
BOT_USERNAME = os.getenv("BOT_USERNAME", "NagiOSINTPROBot")
