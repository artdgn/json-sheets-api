import time
from typing import List, Dict

import requests


class Client:
    """
    API docs at: https://www.coingecko.com/en/api#explore-api

    also possible to use https://github.com/man-c/pycoingecko instead
    """
    ADDRESS = 'https://api.coingecko.com/api/v3/'

    # cache management
    CACHE_TTL_SEC = 86400  # 1 day
    _cache_time: float = 0

    # lazy loading and class state
    _coins: List[dict] = None
    _sym_to_id: Dict[str, str] = None
    _id_to_sym: Dict[str, str] = None

    def _load_coins_data(self):
        if (time.time() - self._cache_time) > self.CACHE_TTL_SEC:
            self._coins = requests.get(f'{self.ADDRESS}/coins/list').json()
            self._sym_to_id = {d['symbol'].lower(): d['id'] for d in self._coins}
            self._id_to_sym = {d['id']: d['symbol'] for d in self._coins}

    def _symbols_to_ids(self, symbols: List[str]):
        self._load_coins_data()
        ids = []
        for sym in symbols:
            id = self._sym_to_id.get(sym.lower())
            if not id:
                raise ValueError(f'"{sym.lower()}" not found in CoinGecko ids')
            ids.append(id)
        return ids

    def prices_for_symbols(self, symbols: List[str], currency: str) -> List[float]:
        """
        :param symbols: list of ticker symbol strings (e.g. `btc`) that are
            translated to CoinGecko ids (e.g. `bitcoin`) to make the requests.
        :param currency: e.g. `usd`
        :return: list of floats
        """
        currency = currency.lower()
        ids = self._symbols_to_ids(symbols)
        print('  ids:')
        print('\n'.join([str(id) for id in ids]))
        res = requests.get(
            f'{self.ADDRESS}/simple/price',
            params={
                'ids': ','.join(ids),
                'vs_currencies': currency,
            }).json()
        return [res[id][currency] for id in ids]
