import logging

import fastapi
from starlette import responses
import xmltodict

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

