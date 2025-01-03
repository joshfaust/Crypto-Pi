from typing import Dict, List, Optional, Tuple, Union
import time
from pathlib import Path
from configparser import ConfigParser
from src.ticker_display import TickerDisplay
from src.crypto import CryptoTickers

COIN_ENUM = {
    "bitcoin": "BTC",
    "cardano": "ADA",
    "ethereum": "ETH",
    "ripple": "XRP",
    "matic-network": "MATIC"
}

def get_coin_data() -> List[Dict]:
    parser = ConfigParser()
    parser.read("secrets.ini")
    key = parser['cg']['key']

    ct = CryptoTickers(coin_gecko_api_key=key)
    coins = ["bitcoin", "cardano", "ethereum", "ripple", "matic-network"]
    cd = ct.get_coin_price(coins, "usd")

    final_coin_data = []
    for coin, coin_data in cd.items():
        ticker_symbol = COIN_ENUM[coin]
        data = {
            "symbol": ticker_symbol,
            "price": coin_data.get("usd"),
            "change": coin_data.get("usd_24h_change"),
            "volume": coin_data.get("usd_24h_vol")
        }
        final_coin_data.append(data)
    return final_coin_data


def write_to_display() -> None:
    display = TickerDisplay()

    try:
        while True:
            tickers = get_coin_data()
            display.clear()
            display.draw_header()

            for i, ticker in enumerate(tickers):
                display.draw_ticker(
                    position=(10, 45 + i * 55),
                    symbol=str(ticker["symbol"]),
                    price=float(ticker["price"]),
                    change=float(ticker["change"]),
                    volume=float(ticker["volume"])
                )
            
            display.update_display()
            five_min = 60 * 5
            time.sleep(five_min)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error in write_to_display(): {e}")
        display.draw_static_elements(tickers)

if __name__ == "__main__":
    write_to_display()
