import logging

import fastapi
from starlette import responses
import xmltodict

from proxy import coingecko

logger = logging.getLogger(__name__)

app = fastapi.FastAPI()


@app.get("/xml/price/{ticker}", response_class=responses.PlainTextResponse)
def xml_price(ticker: str, currency: str = 'usd') -> str:
    """
    Return price for ticker symbol in XML format for usage in google sheets.

    :param ticker: ticker symbol
    :param currency: currency for price
    :return: XML with just "price" as the only element

    Example usage ins sheets:
        `=importxml("https://your-api-public-domain.io/xml/price/btc","result")`
    """
    try:
        prices = coingecko.Client().prices_for_symbols([ticker], currency=currency)
        result = prices[0]
    except Exception as e:
        result  = f'Error: {str(e)}'
    return xmltodict.unparse({'result': result}, pretty=True)

