import asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp

BOT_TOKEN = "7497491886:AAEP9EHAArlzvf3pCCZhMLaQu-yQKnfSyxc"
CHAT_ID = -1002709422757

async def fetch_top_deal():
    url = "https://gg.deals/games/ajax/?ordering=-deal_rating&limit=1"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            if not data or "results" not in data or len(data["results"]) == 0:
                return None
            return data["results"][0]

async def autopost_task():
    bot = Bot(token=BOT_TOKEN)
    game = await fetch_top_deal()
    if not game:
        return

    title = game["title"]
    discount = game["discount"]
    price_old = game["price_old"]
    price_new = game["price_new"]
    link = "https://gg.deals" + game["urls"]["web"]
    image = game["image"]

caption = (
    f"🎮 *{title}*\n"
    f"💸 ~~{price_old}~~ → *{price_new}* ({discount}% OFF)\n"
    f"🔗 [Смотреть на GG.deals]({link})"
)

    buttons = [[InlineKeyboardButton("🔗 Перейти", url=link)]]
    markup = InlineKeyboardMarkup(buttons)

    await bot.send_photo(
        chat_id=CHAT_ID,
        photo=image,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton("🔔 Подписаться на скидки", url="https://t.me/steamlooter")]]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "🎉 *Добро пожаловать!*

"
        "Этот бот присылает горячие скидки на лучшие игры! 🕹
"
        "👇 Нажми, чтобы подписаться на канал со скидками:",
        parse_mode="Markdown",
        reply_markup=markup
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(autopost_task, "interval", minutes=30)
    scheduler.start()

    print("Бот запущен. Ожидание команд и автопостов...")
    app.run_polling()

if __name__ == "__main__":
    main()
