import requests
import time
import threading
from datetime import datetime, timezone
from telegram import Bot

TOKEN = "8758923281:AAG6turoOyFlxhrq-GsMse8n3cBG8QyCdU4"
CHANNEL_ID = "@mmmssaacs"

bot = Bot(token=TOKEN)

cache = {}

LEAGUES = ["esp.1", "uefa.champions", "uefa.europa"]

# 📡 جلب المباريات
def get_matches():
    all_matches = []

    for league in LEAGUES:
        try:
            url = f"https://site.api.espn.com/apis/v2/sports/soccer/{league}/scoreboard"
            res = requests.get(url)
            data = res.json()

            all_matches.extend(data.get("events", []))

        except:
            pass

    return all_matches


# 🔔 إشعارات قبل المباراة
def pre_match():
    while True:
        try:
            matches = get_matches()

            for m in matches:
                comp = m["competitions"][0]

                home = comp["competitors"][0]["team"]["displayName"]
                away = comp["competitors"][1]["team"]["displayName"]

                # 🎯 برشلونة فقط
                if "Barcelona" not in home and "Barcelona" not in away:
                    continue

                match_id = m["id"]

                # ⏰ وقت المباراة
                match_time = datetime.fromisoformat(m["date"].replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)

                diff = (match_time - now).total_seconds() / 60

                print("⏰ الوقت المتبقي:", diff)

                # 🔔 قبل ساعة
                if 55 < diff < 60 and not cache.get(f"{match_id}_60"):
                    cache[f"{match_id}_60"] = True

                    bot.send_message(
                        CHANNEL_ID,
                        f"⏰ بعد ساعة مباراة برشلونة!\n🏟️ {home} vs {away}"
                    )

                # 🔥 قبل 10 دقائق
                if 5 < diff < 10 and not cache.get(f"{match_id}_10"):
                    cache[f"{match_id}_10"] = True

                    bot.send_message(
                        CHANNEL_ID,
                        f"🔥 بعد دقائق!\n🏟️ {home} vs {away}"
                    )

        except Exception as e:
            print("Error:", e)

        time.sleep(60)


# ⚽ البوت الأساسي
def notifications():
    while True:
        try:
            matches = get_matches()

            print("------ CHECKING BARCELONA ------")

            for m in matches:
                comp = m["competitions"][0]

                home = comp["competitors"][0]["team"]["displayName"]
                away = comp["competitors"][1]["team"]["displayName"]

                if "Barcelona" not in home and "Barcelona" not in away:
                    continue

                home_score = int(comp["competitors"][0]["score"])
                away_score = int(comp["competitors"][1]["score"])

                status = m["status"]["type"]["short"]
                match_id = m["id"]

                print("🔥", home, "vs", away, "|", home_score, "-", away_score, "|", status)

                # 🟢 بداية
                if ("H" in status or "LIVE" in status) and match_id not in cache:
                    cache[match_id] = (home_score, away_score)

                    bot.send_message(
                        CHANNEL_ID,
                        f"🟢 بدأت مباراة برشلونة\n🏟️ {home} vs {away}\n⚽ {home_score}-{away_score}"
                    )

                # ⚽ أهداف
                if match_id in cache:
                    old_home, old_away = cache[match_id]

                    if home_score > old_home:
                        bot.send_message(CHANNEL_ID, f"⚽ هدف لـ {home}")

                    if away_score > old_away:
                        bot.send_message(CHANNEL_ID, f"⚽ هدف لـ {away}")

                    cache[match_id] = (home_score, away_score)

                # 🔚 نهاية
                if status == "FT" and not cache.get(f"{match_id}_end"):
                    cache[f"{match_id}_end"] = True

                    bot.send_message(
                        CHANNEL_ID,
                        f"🔚 انتهت مباراة برشلونة\n🏟️ {home} vs {away}\n⚽ {home_score}-{away_score}"
                    )

        except Exception as e:
            print("Error:", e)

        time.sleep(15)


# ▶️ تشغيل
threading.Thread(target=notifications).start()
threading.Thread(target=pre_match).start()

print("🔥 BARCELONA BOT + ALERTS RUNNING 🔥")
