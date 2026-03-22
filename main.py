import requests
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import datetime
import pytz

TOKEN = os.getenv("TOKEN")

# 🌍 التوقيت المحلي
LOCAL_TZ = pytz.timezone("Asia/Riyadh")

# 📊 جلب المباريات
def get_matches():
    url = "https://site.api.espn.com/apis/v2/sports/soccer/eng.1/scoreboard"
    return requests.get(url).json().get("events", [])

# 🔥 /live
def live(update: Update, context: CallbackContext):
    matches = get_matches()
    msg = "🔥 المباريات المباشرة:\n\n"

    found = False

    for match in matches:
        status = match["status"]["type"]["name"]

        if status == "STATUS_IN_PROGRESS":
            comp = match["competitions"][0]

            home = comp["competitors"][0]["team"]["displayName"]
            away = comp["competitors"][1]["team"]["displayName"]

            home_score = comp["competitors"][0]["score"]
            away_score = comp["competitors"][1]["score"]

            msg += f"⚽ {home} {home_score} - {away_score} {away}\n"
            found = True

    if not found:
        msg = "❌ لا توجد مباريات مباشرة الآن"

    update.message.reply_text(msg)

# 📅 /today
def today(update: Update, context: CallbackContext):
    matches = get_matches()
    msg = "📅 مباريات اليوم:\n\n"

    for match in matches:
        comp = match["competitions"][0]

        home = comp["competitors"][0]["team"]["displayName"]
        away = comp["competitors"][1]["team"]["displayName"]

        utc_time = datetime.fromisoformat(match["date"].replace("Z", "+00:00"))
        local_time = utc_time.astimezone(LOCAL_TZ)

        msg += f"⚽ {home} vs {away}\n🕒 {local_time.strftime('%H:%M')}\n\n"

    update.message.reply_text(msg)

# 🚀 تشغيل البوت
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("live", live))
    dp.add_handler(CommandHandler("today", today))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
