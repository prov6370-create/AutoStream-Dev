import asyncio
from aiogram import Bot

TOKEN = "№№№№№№№№№№№№"
CHAT_ID = "№№№№№№№№№№№№№№№№№"


async def send_telegram_alert(game_name, old_price, new_price, diff, url, status):
    bot = Bot(token=TOKEN)

    icon = "📉" if status == "впала" else "📈"
    # Формуємо текст повідомлення
    message = (
        f"{icon} **Ціна {status}!**\n\n"
        f"🎮 **Гра:** {game_name}\n"
        f"💰 Стара ціна: {old_price}\n"
        f"🔥 Нова ціна: {new_price}\n"
        f"💸 Різниця: **{diff} грн**\n\n"
        f"🔗 [Відкрити в Steam]({url})"
    )

    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown", disable_web_page_preview=False)
    finally:
        await bot.session.close()