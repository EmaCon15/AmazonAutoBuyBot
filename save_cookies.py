import asyncio
import pickle
from playwright.async_api import async_playwright # type: ignore

async def save_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Vai alla pagina di login
        await page.goto("https://www.amazon.it/gp/sign-in.html")

        print("➡️ Esegui il login manuale su Amazon (inclusa OTP) e poi premi INVIO qui...")
        input()

        # Ottieni i cookie e salvali
        cookies = await context.cookies()
        with open("amazon_cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)

        print("✅ Cookie salvati in amazon_cookies.pkl")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(save_cookies())
