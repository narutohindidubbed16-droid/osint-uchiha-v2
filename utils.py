import re
import json

# -------------------------------
# JSON Beautifier
# -------------------------------
def clean_json(data):
    """
    Converts raw API JSON into clean readable format
    """
    try:
        if isinstance(data, (str, bytes)):
            try:
                data = json.loads(data)
            except:
                return str(data)
                
        return json.dumps(data, indent=2, ensure_ascii=False)
    except:
        return str(data)

# -------------------------------
# Validate Inputs
# -------------------------------
def validate_input(mode, text):
    text = text.strip().upper()

    patterns = {  
        "mobile": r"^\d{10}$",  
        "gst": r"^[0-9A-Z]{15}$",  
        "ifsc": r"^[A-Z]{4}0[A-Z0-9]{6}$",  
        "pincode": r"^\d{6}$",  
        "vehicle": r"^[A-Z]{2}\d{2}[A-Z]{1,3}\d{3,4}$", 
        "imei": r"^\d{15}$"
    }  

    if mode in patterns and re.fullmatch(patterns[mode], text):  
        return True  
    return False
