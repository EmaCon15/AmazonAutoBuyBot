import threading
import pickle
import os
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from time import sleep
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

class autobuy_bot(threading.Thread):
    def __init__(self, asin, cut_price, autocheckout):
        super().__init__()
        self.amazon_email = os.getenv("AMAZON_EMAIL")
        self.amazon_psw = os.getenv("AMAZON_PSW")
        self.asin = asin
        self.cut_price = cut_price
        self.autocheckout = autocheckout

    def run(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(options=options)

        driver.get("https://www.amazon.it")

        # Prova a caricare i cookie salvati
        cookies_loaded = False
        if os.path.exists("amazon_cookies.pkl"):
            with open("amazon_cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
                cookies_loaded = True

        # Ricarica la pagina dopo aver aggiunto i cookie
        driver.get("https://www.amazon.it/gp/cart/view.html")
        sleep(2)

        # Verifica se il login è riuscito
        try:
            driver.find_element(By.ID, "nav-link-accountList-nav-line-1")
            print(f"[{self.asin}] ✅ Login riuscito con cookie.")
        except:
            print(f"[{self.asin}] ❌ Cookie invalidi o scaduti. Esegui `save_cookies.py` per rigenerarli.")
            driver.quit()
            return

        # Vai alla pagina del prodotto
        driver.get(f"https://www.amazon.it/dp/{self.asin}/ref=olp-opf-redir?aod=1&tag=emacon15-21")
        sleep(2)

        while True:
            try:
                price_element = driver.find_element(By.XPATH, '//*[@id="aod-price-0"]/div/span/span[2]/span[1]')
                current_price = int(price_element.get_attribute("innerHTML").split("<")[0].replace(".", "").replace(",", ""))
            except:
                driver.refresh()
                sleep(2)
                continue

            if current_price > self.cut_price:
                print(f"[{self.asin}] 💰 Prezzo attuale troppo alto: {current_price} > {self.cut_price}")
            else:
                print(f"[{self.asin}] 🛒 Prezzo OK: {current_price} <= {self.cut_price}")
                try:
                    add_btn = driver.find_element(By.XPATH, '//*[@id="a-autoid-2-offer-0"]/span/input')
                    add_btn.click()
                    sleep(1)
                    driver.find_element(By.XPATH, '//*[@id="sc-buy-box-ptc-button"]/span/input').click()
                    sleep(2)

                    if self.autocheckout:
                        driver.find_element(By.XPATH, '//*[@id="submitOrderButtonId"]/span/input').click()
                        print(f"[{self.asin}] ✅ Ordine completato.")
                    else:
                        print(f"[{self.asin}] ✅ Articolo nel carrello, attesa checkout manuale.")
                except Exception as e:
                    print(f"[{self.asin}] ❌ Errore durante acquisto: {e}")
                break

            sleep(1)
            driver.refresh()

        driver.quit()


# --- CONFIGURAZIONE ---

asin_list = [
    "B0DTQCBW9B",   # Bundle Evoluzioni Prismatiche
    "B0C8NR3FPG",   # Bundle 151
    "B0DW4H2J4Z",   # ETB Avventure
    "B0DX2K9KKZ",   # Super Premium Prismatiche
]

cut_prices = [36,
                36,
                55,
                100]

autocheckouts = [True,
                True,
                True,
                True]

threads = []
for i in range(len(asin_list)):
    bot = autobuy_bot(asin_list[i], cut_prices[i], autocheckouts[i])
    bot.start()
    threads.append(bot)

for t in threads:
    t.join()
