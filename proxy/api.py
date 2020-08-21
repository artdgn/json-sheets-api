import logging

import fastapi
from starlette import responses
import xmltodict
import requests

from proxy import coingecko

logger = logging.getLogger(__name__)

app = fastapi.FastAPI(title='CoinGecko XML proxy')


@app.get('/', response_class=responses.HTMLResponse)
def health():
    """Just a welcome text"""
    return """
        Welcome!<br>
        <a href="/docs">Docs UI</a>?<br>
        <a href="https://github.com/artdgn/coingecko-sheets" target="_blank">GitHub</a>?
        """


@app.get("/xml/price/{ticker}", response_class=responses.PlainTextResponse)
def xml_price(ticker: str, currency: str = 'usd') -> str:
    """
    Return price for ticker symbol in XML format for usage in google sheets.

    :param ticker: ticker symbol
    :param currency: currency for price
    :return: XML with just "price" as the only element

    Example usage in sheets:
        `=importxml("https://your-api-address/xml/price/btc","result")`
    """
    try:
        prices = coingecko.Client().prices_for_symbols([ticker], currency=currency)
        result = prices[0]
    except Exception as e:
        result  = f'error: {str(e)}'
    return xmltodict.unparse({'result': result}, pretty=True)


@app.get("/xml/get", response_class=responses.PlainTextResponse)
def xml_get_json(url: str) -> str:
    """
    GET any JSON from any API and encode it as XML. 

    :param url: url path with parameters already encoded
    :return: JSON response encoded as XML under the root "result" field.

    Example usage in sheets if you want to query the Chuck Norris jokes API
        for a random dirty joke and get the joke value:
        `=importxml("https://your-api-address/xml/get?url=https://api.icndb.com/jokes/random?limitTo=[explicit]","result/value/joke")`
    """
    try:
        response = requests.get(url)
        if response.ok:
            result = response.json()
        else:
            result = f'got {response.status_code} for {url}: {response.text}'
    except Exception as e:
        result  = f'error: {str(e)}'
    return xmltodict.unparse({'result': result}, pretty=True)
