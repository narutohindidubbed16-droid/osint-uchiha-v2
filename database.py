import json
import os
from config import START_CREDITS

DB_FILE = "database.json"

# ------------------------------
# Load Database
# ------------------------------
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            f.write("{}")
    with open(DB_FILE, "r") as f:
        return json.load(f)

# ------------------------------
# Save Database
# ------------------------------
def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

# ------------------------------
# Create New User
# ------------------------------
def create_user(user_id, username, name):
    db = load_db()

    if str(user_id) not in db:  
        db[str(user_id)] = {  
            "username": username,  
            "name": name,  
            "credits": START_CREDITS,  
            "referrals": []  
        }  
        save_db(db)  
        return True  
    return False 

# ------------------------------
# Get Credits
# ------------------------------
def get_user_credits(user_id):
    db = load_db()
    return db.get(str(user_id), {}).get("credits", 0)

# ------------------------------
# Decrease Credit
# ------------------------------
def decrease_credit(user_id):
    db = load_db()
    if str(user_id) in db:
        db[str(user_id)]["credits"] -= 1
        if db[str(user_id)]["credits"] < 0:
            db[str(user_id)]["credits"] = 0
        save_db(db)

# ------------------------------
# Add Referral
# ------------------------------
def add_referral(referrer_id, user_id):
    db = load_db()
    if str(referrer_id) in db:
        if user_id not in db[str(referrer_id)]["referrals"]:
            db[str(referrer_id)]["referrals"].append(user_id)
            db[str(referrer_id)]["credits"] += 1
            save_db(db)

# ------------------------------
# Admin: Add Credits
# ------------------------------
def admin_add_credits(user_id, amount):
    db = load_db()
    if str(user_id) in db:
        db[str(user_id)]["credits"] += amount
        save_db(db)
        return True
    return False

# ------------------------------
# Admin: Remove Credits
# ------------------------------
def admin_remove_credits(user_id, amount):
    db = load_db()
    if str(user_id) in db:
        db[str(user_id)]["credits"] -= amount
        if db[str(user_id)]["credits"] < 0:
            db[str(user_id)]["credits"] = 0
        save_db(db)
        return True
    return False

# ------------------------------
# Admin: List all users
# ------------------------------
def get_all_users():
    db = load_db()
    return db
  
