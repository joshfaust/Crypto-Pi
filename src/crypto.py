import requests
import json

class CryptoTickers:

    def __init__(self, coin_gecko_api_key: str):
        self.session = requests.Session()
        self.base_domain = "https://api.coingecko.com/api/v3/"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": coin_gecko_api_key
        }
        self.session.headers = headers

    def _get(self, uri: str, params: dict = {}) -> json:
        formatted_params = {
            k: str(v).lower() if isinstance(v, bool) else v 
            for k, v in params.items()
        }
        return self.session.get(uri, params=formatted_params)
    
    def get_coin_price(self, coin_ids: list, base_currency: str = "usd") -> json:
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": base_currency,
            "include_market_cap": False,
            "include_24hr_vol": True,
            "include_24hr_change": True,
            "include_last_updated_at": False,
            "precision": 2
        }
        uri = f"{self.base_domain}simple/price"
        r = self._get(uri, params)
        return r.json()
