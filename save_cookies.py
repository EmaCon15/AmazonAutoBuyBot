import asyncio
import json
import base64
from playwright.async_api import async_playwright  # type: ignore

async def save_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Vai alla pagina di login
        await page.goto("https://www.amazon.it/gp/sign-in.html")

        print("➡️ Please log in manually to Amazon (including OTP) and then press ENTER here...")
        input()

        # Ottieni i cookie e salvali
        cookies = await context.cookies()

        # Salva in file JSON per sicurezza
        with open("amazon_cookies.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)

        # Codifica in base64 per inserire in variabile ENV
        cookies_json = json.dumps(cookies)
        cookies_b64 = base64.b64encode(cookies_json.encode("utf-8")).decode("utf-8")

        print("\n✅ Cookies saved in amazon_cookies.json")
        print("📋 Copy this string and use it in the COOKIE_B64 variable on Railway:\n")
        print(cookies_b64)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(save_cookies())
