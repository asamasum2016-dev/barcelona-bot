import requests
import time
import os
import threading
import asyncio
from telegram import Bot
from flask import Flask

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

async def send(msg):
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=msg)
    except Exception as e:
        print("Send error:", e)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

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
                    loop.run_until_complete(send(f"🔥 {home} vs {away}\n{home_score}-{away_score}"))

                else:
                    old_home, old_away = cache[match_id]

                    if home_score != old_home or away_score != old_away:
                        loop.run_until_complete(send(f"⚽ تحديث\n{home} {home_score}-{away_score} {away}"))

                    cache[match_id] = (home_score, away_score)

        except Exception as e:
            print("Error:", e)

        time.sleep(20)

# Flask server (مهم لـ Railway)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running 🔥"

def run_web():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_bot).start()
run_web()
