import requests
import time
import os
from telegram import Bot
from datetime import datetime, timedelta
import pytz

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=TOKEN)

sent_matches = set()
live_matches = {}
sent_goals = set()

# 🌍 التوقيت المحلي (غيّرها إذا تبغى)
LOCAL_TZ = pytz.timezone("Asia/Riyadh")

def send(msg):
    bot.send_message(chat_id=CHANNEL_ID, text=msg)

def get_matches():
    url = "https://site.api.espn.com/apis/v2/sports/soccer/eng.1/scoreboard"
    return requests.get(url).json().get("events", [])

def get_goals(match_id):
    url = f"https://site.api.espn.com/apis/v2/sports/soccer/eng.1/summary?event={match_id}"
    data = requests.get(url).json()

    goals = []

    try:
        plays = data["plays"]

        for play in plays:
            if play.get("type", {}).get("text") == "Goal":
                minute = play.get("clock", {}).get("displayValue", "??")
                player = play.get("athletesInvolved", [{}])[0].get("displayName", "لاعب")

                goals.append((minute, player))
    except:
        pass

    return goals

def check_matches():
    while True:
        matches = get_matches()

        for match in matches:
            comp = match["competitions"][0]

            home = comp["competitors"][0]["team"]["displayName"]
            away = comp["competitors"][1]["team"]["displayName"]

            match_id = match["id"]
            status = match["status"]["type"]["name"]

            # 🕒 تحويل الوقت إلى المحلي
            utc_time = datetime.fromisoformat(match["date"].replace("Z", "+00:00"))
            local_time = utc_time.astimezone(LOCAL_TZ)
            now = datetime.now(LOCAL_TZ)

            # 🔔 قبل المباراة 15 دقيقة
            if 0 < (local_time - now).total_seconds() <= 900:
                if match_id not in sent_matches:
                    send(f"⏳ بعد 15 دقيقة!\n🔥 {home} vs {away}\n🕒 {local_time.strftime('%H:%M')}")
                    sent_matches.add(match_id)

            # ⚽ المباراة شغالة
            if status == "STATUS_IN_PROGRESS":
                home_score = comp["competitors"][0]["score"]
                away_score = comp["competitors"][1]["score"]

                score = f"{home} {home_score} - {away_score} {away}"

                if match_id not in live_matches:
                    send(f"🚨 بدأت المباراة!\n{score}")
                    live_matches[match_id] = score
                else:
                    if live_matches[match_id] != score:
                        send(f"📊 تحديث:\n{score}")
                        live_matches[match_id] = score

                # 🔥 الأهداف
                goals = get_goals(match_id)

                for minute, player in goals:
                    goal_id = f"{match_id}-{minute}-{player}"

                    if goal_id not in sent_goals:
                        send(f"⚽ هدف!\n👤 {player}\n⏱️ {minute}\n🏟️ {home} vs {away}")
                        sent_goals.add(goal_id)

        time.sleep(30)

if __name__ == "__main__":
    send("🔥 البوت يعمل - نسخة PRO")
    check_matches()
