import requests
import json

class CryptoTickers:

    def __init__(self, coin_gecko_api_key: str):
        """
        CrytoTickers init method

        Args:
            coin_gecko_api_key (str): Your CoinGecko API key
        """
        self.session = requests.Session()
        self.base_domain = "https://api.coingecko.com/api/v3/"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": coin_gecko_api_key
        }
        self.session.headers = headers

    def _get(self, uri: str, params: dict = {}) -> json:
        """
        HTTP Get requests

        Args:
            uri (str): URI
            params (dict, optional): GET parameters. Defaults to {}.

        Returns:
            json: JSON results
        """
        formatted_params = {
            k: str(v).lower() if isinstance(v, bool) else v 
            for k, v in params.items()
        }
        return self.session.get(uri, params=formatted_params)
    
    def get_coin_price(self, coin_ids: list, base_currency: str = "usd") -> json:
        """
        Given a list of coin ids (per the CoinGecko API), retrieve their volume, change %
        and current price

        Args:
            coin_ids (list): CoinGecko coin Ids
            base_currency (str, optional): Currency to pull values. Defaults to "usd".

        Returns:
            json: List[Dict] where each key is the coin id and value is a dict
        """
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
