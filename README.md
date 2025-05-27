# AmazonAutoBuyBot
## Description
A Python bot that uses Selenium to automatically monitor and optionally purchase discounted products or pricing errors on Amazon.

This script is an enhanced and updated version of the original code by @davildf, designed to be more reliable and scalable.

It supports multiple products simultaneously. For each product, you can define:
- A maximum price you're willing to pay.
- Whether the bot should auto-checkout or stop after adding the product to your cart.
- Persistent login via saved cookies (supporting 2FA).

## Main differences from the original code
- ✅ Support for multiple ASINs with configurable price thresholds and checkout options.
- 🔐 Secure login using cookies, allowing persistent sessions even with 2FA enabled.
- 💾 Introduced save_cookies.py to handle manual login (with 2FA) and save cookies in amazon_cookies.json.
- ⚙️ Environment variable support via .env file (using python-dotenv).
  
  🔐 *This means your Amazon credentials are no longer hardcoded in the script but safely stored in a separate `.env` file that is not tracked by version control (i.e., Git). This greatly improves security and makes the code safer to share or use across environments.*
- 🌍 Support for loading cookies from a base64-encoded environment variable COOKIE_B64 (useful for deployment on platforms like Railway).
- 💻 Improved logging with ASINs clearly labeled in output.
- 🧼 Cleaner codebase, better error handling, and easier configuration.

## Getting Started
### Dependencies
  1. Python 3.9.9+
  2. Google Chrome
  3. [ChromeDriver](https://developer.chrome.com/docs/chromedriver/downloads?hl=it) compatible with your Chrome version
### Installing
  ```bash
  git clone https://github.com/EmaCon15/AmazonAutoBuyBot.git
  cd AmazonAutoBuyBot
  pip install -r requirements.txt
  ```
### Running Script
  1. Create a `.env` file in the root directory (same level as main.py) with:

  ``` 
  AMAZON_EMAIL=your_amazon_email
  AMAZON_PSW=your_amazon_password
  COOKIE_B64= # (see below)
  ```
  
  2. Run the login script only once to save cookies:
  ```bash
  python3 save_cookies.py
  ```
  This opens a Chrome window for login. Complete the login manually (including 2FA if enabled). Cookies will be saved to amazon_cookies.json and reused in future runs.

  Cookies will be saved to `amazon_cookies.json`, and in the bash you have the base64 encoded version of the cookies.
  You can then:
  - Copy and paste the base64 econded version in the COOKIE_B64 variable of the `.env` file.
  - Set it as the environment variable COOKIES_B64 for deployment on platforms like Railway.

  3. Open main.py and edit these lists:
  ```python
  asin_list = [ "B0DTQCBW9B", "B0C8NR3FPG" ]          # ASINs to monitor
  cut_prices = [ 36, 36 ]                             # Max prices for each ASIN
  autocheckouts = [ True, False ]                     # Enable auto-checkout per item
  ```
### Running the bot
After configuration:
```bash
python3 main.py
```
Each product will be monitored in a separate thread. If the price drops below your threshold, the item is added to the cart. If `autocheckout`=True, the bot will attempt to place the order automatically.
# Disclaimer
As an Amazon Associate, I earn from qualifying purchases.
The ASIN URLs used in this script contain my affiliate tag (emacon15-21). If you prefer not to use it, you can simply remove the &tag=emacon15-21 from the product links in main.py.
# License
This project is licensed under the MIT License - see the LICENSE.md file for details