import os
from pymongo import MongoClient
from config import START_CREDITS

# ================================
# 🔗 CONNECT MONGO DATABASE
# ================================
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)

# Database name (default)
db = client["osint_uchiha"]

# Collection name
users = db["users"]


# ================================
# 📌 CREATE NEW USER
# ================================
def create_user(user_id, username, name):
    user_id = str(user_id)

    if users.find_one({"user_id": user_id}):
        return False   # user already exists

    users.insert_one({
        "user_id": user_id,
        "username": username,
        "name": name,
        "credits": START_CREDITS,
        "referrals": []
    })

    return True


# ================================
# 📌 GET USER CREDITS
# ================================
def get_user_credits(user_id):
    user_id = str(user_id)
    user = users.find_one({"user_id": user_id})

    if not user:
        return 0

    return user.get("credits", 0)


# ================================
# 📌 DECREASE CREDIT
# ================================
def decrease_credit(user_id):
    user_id = str(user_id)
    users.update_one(
        {"user_id": user_id},
        {"$inc": {"credits": -1}}
    )


# ================================
# 📌 ADD REFERRAL (+1 CREDIT)
# ================================
def add_referral(referrer_id, new_user_id):
    referrer_id = str(referrer_id)

    ref = users.find_one({"user_id": referrer_id})
    if not ref:
        return False

    # Avoid duplicate referrals
    if new_user_id not in ref.get("referrals", []):
        users.update_one(
            {"user_id": referrer_id},
            {
                "$push": {"referrals": new_user_id},
                "$inc": {"credits": 1}
            }
        )

    return True


# ================================
# 📌 ADMIN: ADD CREDITS
# ================================
def admin_add_credits(user_id, amount):
    user_id = str(user_id)

    if not users.find_one({"user_id": user_id}):
        return False

    users.update_one(
        {"user_id": user_id},
        {"$inc": {"credits": amount}}
    )
    return True


# ================================
# 📌 ADMIN: REMOVE CREDITS
# ================================
def admin_remove_credits(user_id, amount):
    user_id = str(user_id)

    if not users.find_one({"user_id": user_id}):
        return False

    users.update_one(
        {"user_id": user_id},
        {"$inc": {"credits": -amount}}
    )
    return True


# ================================
# 📌 ADMIN: GET ALL USERS
# ================================
def get_all_users():
    all_users = list(users.find())
    clean_data = {}

    for u in all_users:
        uid = u.get("user_id")
        clean_data[uid] = {
            "username": u.get("username"),
            "name": u.get("name"),
            "credits": u.get("credits"),
            "referrals": u.get("referrals", [])
        }

    return clean_data
