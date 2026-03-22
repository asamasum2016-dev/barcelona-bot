import requests
import time
import threading
import os
from datetime import datetime, timezone
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=TOKEN)

cache = {}

def get_matches():
    try:
        url = "https://site.api.espn.com/apis/v2/sports/soccer/esp.1/scoreboard"
        return requests.get(url).json().get("events", [])
    except:
        return []

def run_bot():
    while True:
        try:
            matches = get_matches()

            for m in matches:
                comp = m["competitions"][0]

                home = comp["competitors"][0]["team"]["displayName"]
                away = comp["competitors"][1]["team"]["displayName"]

                if "Barcelona" not in home and "Barcelona" not in away:
                    continue

                home_score = int(comp["competitors"][0]["score"])
                away_score = int(comp["competitors"][1]["score"])

                match_id = m["id"]

                if match_id not in cache:
                    cache[match_id] = (home_score, away_score)
                    bot.send_message(chat_id=CHANNEL_ID, text=f"🔥 {home} vs {away}\n{home_score}-{away_score}")

                else:
                    old_home, old_away = cache[match_id]

                    if home_score != old_home or away_score != old_away:
                        bot.send_message(chat_id=CHANNEL_ID, text=f"⚽ تحديث\n{home} {home_score}-{away_score} {away}")

                    cache[match_id] = (home_score, away_score)

        except Exception as e:
            print("Error:", e)

        time.sleep(20)

# Flask (لتشغيل Railway)
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running 🔥"

def run_web():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_bot).start()
run_web()
