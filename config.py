import os

# ==============================
# 🔐 TELEGRAM BOT TOKEN
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")


# ==============================
# 📢 CHANNELS (USERNAME + ID SAFE)
# ==============================
# IMPORTANT:
# 1) Public channel → @username (NO https link)
# 2) Private invite link → full link (https://t.me/+abc123)
# 3) Backup channel → @username
# 4) DO NOT use +hyVTT... as MAIN/BACKUP (invite link cannot be used for getChatMember)

MAIN_CHANNEL = os.getenv("MAIN_CHANNEL")        # e.g., @AbdulBotz
BACKUP_CHANNEL = os.getenv("BACKUP_CHANNEL")    # e.g., @darknagibackup
PRIVATE_CHANNEL = os.getenv("PRIVATE_CHANNEL")  # e.g., https://t.me/+hyVTTQkFJS4lNTFl


# ==============================
# 🌐 API URLs
# ==============================
MOBILE_API = os.getenv("MOBILE_API")
GST_API = os.getenv("GST_API")
IFSC_API = os.getenv("IFSC_API")
PINCODE_API = os.getenv("PINCODE_API")
VEHICLE_API = os.getenv("VEHICLE_API")
RC_API = os.getenv("RC_API")     # FIXED — Earlier mistake: it was VEHICLE_API
IMEI_API = os.getenv("IMEI_API")


# ==============================
# ⚙ ADMIN + CREDITS
# ==============================
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
START_CREDITS = int(os.getenv("START_CREDITS", "5"))


# ==============================
# 🤖 BOT INFO
# ==============================
BOT_USERNAME = os.getenv("BOT_USERNAME", "OsintUchihaProBot")
