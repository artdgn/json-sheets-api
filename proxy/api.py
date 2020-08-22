import logging
from typing import Union

import fastapi
import jsonpath_ng
import requests
import xmltodict
from starlette import responses

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
        prices, _ = coingecko.Client().prices_for_symbols([ticker], currency=currency)
        result = prices[0]
    except Exception as e:
        result = f'error: {str(e)}'
    return xmltodict.unparse({'result': result}, pretty=True)


@app.get("/xml/get", response_class=responses.PlainTextResponse)
def xml_get_json(url: str, request: fastapi.Request, jsonpath: str = None) -> str:
    """
    GET any JSON from any API and encode it as XML, optionally extracting
    parts from it using [JSONPath](https://goessner.net/articles/JsonPath/).

    :param url: url path with parameters already encoded

    :param jsonpath: optional [jsonpath](https://goessner.net/articles/JsonPath/)
        to apply to resulting JSON before encoding as XML
        in case resulting JSON is not a valid XML (or just to simplify xpath decoding)

    :return: JSON response encoded as XML under the root "result" field.

    Example usage in sheets if you want to query the Chuck Norris jokes API
        for a random dirty joke and get the joke value:
        ````=importxml("https://your-api-address/xml/get?
            url=https://api.icndb.com/jokes/random?limitTo=[explicit]",
            "result/value/joke")```
    Same example but using JSONPath:
        ````=importxml("https://your-api-address/xml/get?
            url=https://api.icndb.com/jokes/random?limitTo=[explicit]&jsonpath=value.joke",
            "result")```
    """

    # extract any query params that are not captured by the `url`
    # parameter (e.g. because of `&` splitting
    additional_params = {k: v for k, v in request.query_params.items()
                         if k not in ['url', 'jsonpath']}

    # get the data
    try:
        response = requests.get(url, params=additional_params)
        if response.ok:
            result = response.json()
            if jsonpath:
                result = _apply_jsonpath(result, jsonpath)
        else:
            raise fastapi.HTTPException(response.status_code, response.text)
    except Exception as e:
        result = f'error: {str(e)}'

    # ensure single root
    if isinstance(result, list):
        single_root = {'result': {'items': result}}
    else:
        single_root = {'result': result}
    return xmltodict.unparse(single_root, pretty=True)


def _apply_jsonpath(result: Union[dict, list], jsonpath: str) -> Union[dict, list]:
    """ applies jsonpath expression or add the error that resulted from trying """
    try:
        values = [match.value for match in jsonpath_ng.parse(jsonpath).find(result)]
        if len(values) == 1:
            result = values[0]
        elif not len(values):
            raise IndexError(f'match for {jsonpath} not found')
        else:
            result = values
    except Exception as e:
        err_info = {'jsonpath-error': str(e)}
        if isinstance(result, dict):
            result.update(err_info)
        else:
            result.append(err_info)
        logger.error(f'jsonpath error: {e}')
    return result
