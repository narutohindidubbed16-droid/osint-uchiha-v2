import os
import logging
import threading
from flask import Flask
from waitress import serve

logger = logging.getLogger("keep_alive")

PORT = int(os.environ.get("PORT", 10000))

app = Flask(__name__)

@app.route("/")
def home():
    return "OK", 200

def run_server():
    logger.info(f"[KeepAlive] Starting Waitress server on port {PORT}…")
    serve(app, host="0.0.0.0", port=PORT)

def keep_alive():
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    logger.info("[KeepAlive] Keep-alive thread started successfully.")
