from selenium import webdriver
import pickle
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Impostazioni
options = Options()
options.headless = False  # Deve essere visibile per il login manuale
driver = webdriver.Chrome(options=options)

# Vai alla pagina di login
driver.get("https://www.amazon.it/gp/sign-in.html")

# Aspetta che tu faccia login manualmente
print("➡️ Esegui il login manuale su Amazon (inclusa OTP) e poi premi INVIO qui...")
input()

# Salva i cookie dopo il login
with open("amazon_cookies.pkl", "wb") as f:
    pickle.dump(driver.get_cookies(), f)

print("✅ Cookie salvati in amazon_cookies.pkl")
driver.quit()
