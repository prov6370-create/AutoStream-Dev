import asyncio
import os
import re
import pandas as pd
from playwright.async_api import async_playwright
from TG_Boot import send_telegram_alert

DB_FILE = "steam_prices.csv"


async def get_steam_data(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until="networkidle")

        # Перевірка віку (id селекторів з твого скріншоту)
        if await page.query_selector('#ageYear'):
            await page.select_option('#ageYear', '2000')
            await page.click('#view_product_page_btn')
            await page.wait_for_selector('#appHubAppName')

        name = await page.inner_text('#appHubAppName')

        # Шукаємо актуальну ціну
        price_selectors = [
            ".game_area_purchase_game_wrapper .discount_final_price",
            ".game_area_purchase_game_wrapper .game_purchase_price"
        ]

        price_text = "0"
        for sel in price_selectors:
            el = await page.query_selector(sel)
            if el:
                price_text = await el.inner_text()
                break

        # ОЧИЩЕННЯ ЦІНИ: видаляємо все, крім цифр
        # Це перетворить "59₴" або "59,00 грн" просто в число 59
        numeric_str = re.sub(r'\D', '', price_text)
        current_numeric = int(numeric_str) if numeric_str else 0

        await browser.close()
        return name.strip(), price_text.strip(), current_numeric


async def monitor_price():
    url = "https://store.steampowered.com/app/1238840/Battlefield_1"
    name, current_price_str, current_price_num = await get_steam_data(url)

    # Якщо файл існує, порівнюємо
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            old_price_num = int(df.iloc[0]['NumericPrice'])
            old_price_str = str(df.iloc[0]['DisplayPrice'])

            # Рахуємо різницю
            diff = current_price_num - old_price_num

            # ВІДПРАВЛЯЄМО ТІЛЬКИ ЯКЩО ЦІНА РЕАЛЬНО ЗМІНИЛАСЯ
            if diff < 0:
                print(f"Ціна впала на {abs(diff)}")
                await send_telegram_alert(name, old_price_str, current_price_str, abs(diff), url, "впала")
            elif diff > 0:
                print(f"Ціна виросла на {diff}")
                await send_telegram_alert(name, old_price_str, current_price_str, diff, url, "виросла")
            else:
                print("Змін немає. Повідомлення не відправлено.")
        except Exception as e:
            print(f"Помилка при читанні бази: {e}")
    else:
        print("База порожня. Зберігаємо поточну ціну для наступного разу.")

    # Оновлюємо дані в CSV
    new_df = pd.DataFrame([{
        "Title": name,
        "DisplayPrice": current_price_str,
        "NumericPrice": current_price_num
    }])
    new_df.to_csv(DB_FILE, index=False)


if __name__ == "__main__":
    asyncio.run(monitor_price())