import threading
import os
import asyncio
import base64
import json
from dotenv import load_dotenv  # type: ignore
from playwright.async_api import async_playwright  # type: ignore

load_dotenv()

class AutoBuyBot(threading.Thread):
    def __init__(self, asin, cut_price, autocheckout):
        super().__init__()
        self.amazon_email = os.getenv("AMAZON_EMAIL")
        self.amazon_psw = os.getenv("AMAZON_PSW")
        self.cookie_b64 = os.getenv("COOKIE_B64", "")
        self.asin = asin
        self.cut_price = cut_price
        self.autocheckout = autocheckout

    def run(self):
        asyncio.run(self.async_run())

    async def async_run(self):
        async with async_playwright() as p:
            # Aggiungo argomenti per far girare Chromium in ambiente container senza sandbox
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = await browser.new_context()
            page = await context.new_page()

            cookies_loaded = False
            cookies = []

            # Load cookies from base64 ENV
            if self.cookie_b64:
                print(f"[{self.asin}] 🌍 Loading cookies from base64 environment variable.")
                try:
                    decoded_bytes = base64.b64decode(self.cookie_b64)
                    decoded_str = decoded_bytes.decode("utf-8")
                    cookies = json.loads(decoded_str)
                    cookies_loaded = True
                except Exception as e:
                    print(f"[{self.asin}] ❌ Error decoding or parsing cookies from ENV: {e}")
            else:
                print(f"[{self.asin}] ⚠️ No cookies available in ENV.")

            if cookies_loaded:
                try:
                    await context.add_cookies(cookies)
                except Exception as e:
                    print(f"[{self.asin}] ❌ Error adding cookies: {e}")

            # Naviga al carrello con try-except
            try:
                print(f"[{self.asin}] 🌍 Navigating to cart")
                await page.goto("https://www.amazon.it/gp/cart/view.html")
                print(f"[{self.asin}] 🌍 Cart loaded")
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"[{self.asin}] ❌ Error navigating to cart: {e}")
                await browser.close()
                return

            # Verifica login
            try:
                nav_text = await page.inner_text("#nav-link-accountList-nav-line-1")
                print(f"[{self.asin}] ✅ Login successful with cookie: {nav_text}")
            except Exception:
                print(f"[{self.asin}] ❌ Invalid or expired cookies. Run `save_cookies.py` to regenerate them.")
                await browser.close()
                return

            # Naviga alla pagina prodotto con try-except
            try:
                print(f"[{self.asin}] 🌍 Navigating to product page")
                await page.goto(f"https://www.amazon.it/dp/{self.asin}/ref=olp-opf-redir?aod=1&tag=emacon15-21")
                print(f"[{self.asin}] 🌍 Product page loaded")
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"[{self.asin}] ❌ Error navigating to product page: {e}")
                await browser.close()
                return

            while True:
                try:
                    price_element = await page.query_selector('xpath=//*[@id="aod-price-0"]/div/span/span[2]/span[1]')
                    if price_element:
                        raw_price = await price_element.inner_text()
                        # Rimuovo eventuali simboli e formatto il prezzo come int (in centesimi per sicurezza)
                        prezzo_str = raw_price.replace("€", "").replace(".", "").replace(",", ".").strip()
                        current_price = float(prezzo_str)
                    else:
                        raise Exception("Price element not found")
                except Exception as e:
                    print(f"[{self.asin}] ❌ Error reading price: {e}, ricarico pagina...")
                    await page.reload()
                    await page.wait_for_timeout(2000)
                    continue

                if current_price > self.cut_price:
                    print(f"[{self.asin}] 💰 Current price too high: {current_price} > {self.cut_price}")
                else:
                    print(f"[{self.asin}] 🛒 Price OK: {current_price} <= {self.cut_price}")
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
                                    print(f"[{self.asin}] ✅ Order completed.")
                                else:
                                    print(f"[{self.asin}] ❌ Order button not found.")
                            else:
                                print(f"[{self.asin}] ✅ Item in cart, waiting for manual checkout.")
                        else:
                            print(f"[{self.asin}] ❌ Add button not found")
                    except Exception as e:
                        print(f"[{self.asin}] ❌ Error during purchase: {e}")
                    break

                await page.wait_for_timeout(1000)
                await page.reload()

            await browser.close()


# --- CONFIGURATION ---

asin_list = [
    "B0DTQCBW9B",
    "B0C8NR3FPG",
    "B0DW4H2J4Z",
    "B0DX2K9KKZ",
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
