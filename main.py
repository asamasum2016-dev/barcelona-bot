import requests
import time
import os
import threading
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=TOKEN)
bot.send_message(chat_id=CHANNEL_ID, text="🔥 البوت شغال الآن!")
cache = {}

TEAM_NAME = "Barcelona"

# 🧠 جلب المباريات
def get_matches():
    try:
        url = "https://site.api.espn.com/apis/v2/sports/soccer/esp.1/scoreboard"
        return requests.get(url).json().get("events", [])
    except:
        return []

# ⚡ إرسال رسالة
async def send(msg, buttons=None):
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=msg,
            reply_markup=buttons
        )
    except Exception as e:
        print("Send error:", e)

# 🔘 أزرار
def get_buttons(match_id):
    keyboard = [
        [InlineKeyboardButton("📊 الإحصائيات", callback_data=f"stats_{match_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ⚽ النظام الرئيسي
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

                if TEAM_NAME not in home and TEAM_NAME not in away:
                    continue

                home_score = int(comp["competitors"][0]["score"])
                away_score = int(comp["competitors"][1]["score"])
                match_id = m["id"]

                status = m["status"]["type"]["short"]

                # 🟢 بداية المباراة
                if status in ["1H", "2H", "LIVE"] and match_id not in cache:
                    cache[match_id] = (home_score, away_score)

                    loop.run_until_complete(send(
                        f"🟢 بدأت المباراة\n{home} vs {away}\n⚽ {home_score}-{away_score}",
                        get_buttons(match_id)
                    ))

                # ⚽ تحديث الأهداف
                if match_id in cache:
                    old_home, old_away = cache[match_id]

                    if home_score != old_home or away_score != old_away:
                        loop.run_until_complete(send(
                            f"⚽ هدف!\n{home} {home_score}-{away_score} {away}"
                        ))

                    cache[match_id] = (home_score, away_score)

                # 🔚 نهاية المباراة
                if status == "FT" and not cache.get(f"{match_id}_end"):
                    cache[f"{match_id}_end"] = True

                    loop.run_until_complete(send(
                        f"🔚 انتهت المباراة\n{home} {home_score}-{away_score} {away}"
                    ))

        except Exception as e:
            print("Error:", e)

        time.sleep(20)

# 🌐 Flask (مهم لـ Railway)
app = Flask(__name__)

@app.route("/")
def home():
    return "SofaScore Bot Running 🔥"

def run_web():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_bot).start()
run_web()
