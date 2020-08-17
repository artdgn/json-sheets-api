from typing import List, Dict

import requests


class Client:
    """
    API docs at: https://www.coingecko.com/en/api#explore-api
    """
    ADDRESS = 'https://api.coingecko.com/api/v3/'

    _coins: List[dict] = None
    _sym_to_id: Dict[str, str] = None
    _id_to_sym: Dict[str, str] = None

    def _load_coins_data(self):
        if self._coins is None:
            self._coins = requests.get(f'{self.ADDRESS}/coins/list').json()
            self._sym_to_id = {d['symbol'].lower(): d['id'] for d in self._coins}
            self._id_to_sym = {d['id']: d['symbol'] for d in self._coins}

    @property
    def symbol_id_map(self):
        self._load_coins_data()
        return self._sym_to_id

    def prices_for_symbols(self, symbols: str, currency: str) -> List[float]:
        ids = list(map(self.symbol_id_map.get, symbols.lower().split()))
        res = requests.get(
            f'{self.ADDRESS}/simple/price',
            params={
                'ids': ','.join(ids),
                'vs_currencies': currency,
            }).json()
        return [res[id][currency] for id in ids]
