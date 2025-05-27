import threading
import pickle
import os
import asyncio
import base64
import io
from dotenv import load_dotenv  # type: ignore
from playwright.async_api import async_playwright # type: ignore

load_dotenv()

class AutoBuyBot(threading.Thread):
    def __init__(self, asin, cut_price, autocheckout):
        super().__init__()
        self.amazon_email = os.getenv("AMAZON_EMAIL")
        self.amazon_psw = os.getenv("AMAZON_PSW")
        self.cookie_b64 = os.getenv("AMAZON_COOKIES_B64", "")
        self.asin = asin
        self.cut_price = cut_price
        self.autocheckout = autocheckout

    def run(self):
        asyncio.run(self.async_run())

    async def async_run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Try to upload saved cookies
            cookie_file_path = "amazon_cookies.pkl"
            cookies_loaded = False

            if os.path.exists(cookie_file_path):
                print(f"[{self.asin}] 📦 Caricamento cookie da file locale.")
                with open(cookie_file_path, "rb") as f:
                    cookies = pickle.load(f)
                cookies_loaded = True
            elif self.cookie_b64:
                print(f"[{self.asin}] 🌍 Caricamento cookie da variabile d'ambiente base64.")
                try:
                    decoded = base64.b64decode(self.cookie_b64)
                    cookies = pickle.load(io.BytesIO(decoded))
                    cookies_loaded = True
                except Exception as e:
                    print(f"[{self.asin}] ❌ Errore nel decoding dei cookie da ENV: {e}")
            else:
                print(f"[{self.asin}] ⚠️ Nessun cookie disponibile.")

            if cookies_loaded:
                await page.goto("https://www.amazon.it")
                await context.add_cookies([{
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c.get("domain", ".amazon.it"),
                    "path": c.get("path", "/"),
                    "httpOnly": c.get("httpOnly", False),
                    "secure": c.get("secure", True),
                    "sameSite": c.get("sameSite", "Lax"),
                    "expires": -1
                } for c in cookies])

            await page.goto("https://www.amazon.it/gp/cart/view.html")
            await page.wait_for_timeout(2000)

            try:
                nav_text = await page.inner_text("#nav-link-accountList-nav-line-1")
                print(f"[{self.asin}] ✅ Login riuscito con cookie: {nav_text}")
            except:
                print(f"[{self.asin}] ❌ Cookie invalidi o scaduti. Esegui `save_cookies.py` per rigenerarli.")
                await browser.close()
                return

            await page.goto(f"https://www.amazon.it/dp/{self.asin}/ref=olp-opf-redir?aod=1&tag=emacon15-21")
            await page.wait_for_timeout(2000)

            while True:
                try:
                    price_element = await page.query_selector('xpath=//*[@id="aod-price-0"]/div/span/span[2]/span[1]')
                    if price_element:
                        raw_price = await price_element.inner_text()
                        current_price = int(raw_price.split("<")[0].replace(".", "").replace(",", "").strip())
                    else:
                        raise Exception("Elemento prezzo non trovato")
                except:
                    await page.reload()
                    await page.wait_for_timeout(2000)
                    continue

                if current_price > self.cut_price:
                    print(f"[{self.asin}] 💰 Prezzo attuale troppo alto: {current_price} > {self.cut_price}")
                else:
                    print(f"[{self.asin}] 🛒 Prezzo OK: {current_price} <= {self.cut_price}")
                    try:
                        add_btn = await page.query_selector('xpath=//*[@id="a-autoid-2-offer-0"]/span/input')
                        if add_btn:
                            await add_btn.click()
                            await page.wait_for_timeout(1000)
                            checkout_btn = await page.query_selector('xpath=//*[@id="sc-buy-box-ptc-button"]/span/input')
                            if checkout_btn:
                                await checkout_btn.click()
                                await page.wait_for_timeout(2000)

                            if self.autocheckout:
                                order_btn = await page.query_selector('xpath=//*[@id="submitOrderButtonId"]/span/input')
                                if order_btn:
                                    await order_btn.click()
                                    print(f"[{self.asin}] ✅ Ordine completato.")
                            else:
                                print(f"[{self.asin}] ✅ Articolo nel carrello, attesa checkout manuale.")
                    except Exception as e:
                        print(f"[{self.asin}] ❌ Errore durante acquisto: {e}")
                    break

                await page.wait_for_timeout(1000)
                await page.reload()

            await browser.close()


# --- CONFIGURATION ---

asin_list = [
    "B0DTQCBW9B",   # Bundle Evoluzioni Prismatiche
    "B0C8NR3FPG",   # Bundle 151
    "B0DW4H2J4Z",   # ETB Avventure
    "B0DX2K9KKZ",   # Super Premium Prismatiche
]

cut_prices = [36, 36, 55, 100]

autocheckouts = [True, True, True, True]

threads = []
for i in range(len(asin_list)):
    bot = AutoBuyBot(asin_list[i], cut_prices[i], autocheckouts[i])
    bot.start()
    threads.append(bot)

for t in threads:
    t.join()
