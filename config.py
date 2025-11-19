import os

# ==============================
# 🔐 TELEGRAM BOT TOKEN
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")


# ==============================
# 📢 CHANNELS (PUBLIC ONLY)
# ==============================
# IMPORTANT:
# ✔ MAIN_CHANNEL → sirf @username (NO link)
# ✔ BACKUP_CHANNEL → sirf @username (NO link)
# ❌ PRIVATE INVITE LINKS (https://t.me/+xxx) join-check me allowed nahi

MAIN_CHANNEL = os.getenv("MAIN_CHANNEL")        # e.g., @AbdulBotz
BACKUP_CHANNEL = os.getenv("BACKUP_CHANNEL")    # e.g., @darknagibackup

# PRIVATE CHANNEL USED ONLY FOR BUTTON DISPLAY (NO JOIN-CHECK)
PRIVATE_CHANNEL = os.getenv("PRIVATE_CHANNEL")  # optional


# ==============================
# 🌐 API URLs
# ==============================
MOBILE_API = os.getenv("MOBILE_API")
GST_API = os.getenv("GST_API")
IFSC_API = os.getenv("IFSC_API")
PINCODE_API = os.getenv("PINCODE_API")

# Correct mapping — RC = Vehicle lookup API
RC_API = os.getenv("RC_API")  
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
