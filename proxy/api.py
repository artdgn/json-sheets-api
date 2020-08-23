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


@app.get("/coingecko/xml/price/{symbol}", response_class=responses.PlainTextResponse)
def xml_price(symbol: str, currency: str = 'usd') -> str:
    """
    Return price for ticker symbol in XML format for usage in google sheets.

    ### Parameters:
    - symbol: coin (ticker) symbol (e.g. btc)
    - currency: currency for price

    ### Returns:
    XML with just "price" as the only element

    ### Example usage in Sheets:
    `=importxml("https://your-api-address/coingecko/xml/price/btc","result")`
    """
    try:
        prices, _ = coingecko.Client().prices_for_symbols([symbol], currency=currency)
        result = prices[0]
    except Exception as e:
        result = f'error: {str(e)}'
    return xmltodict.unparse({'result': result}, pretty=True)


@app.get("/xml/get", response_class=responses.PlainTextResponse)
def xml_get_json(url: str, _request: fastapi.Request, jsonpath: str = None) -> str:
    """
    GET any JSON from any API and encode it as XML, optionally extracting
    parts from it using [JSONPath](https://goessner.net/articles/JsonPath/).

    ### Parameters:
    - url: url path with parameters already encoded
    - jsonpath: optional [jsonpath](https://goessner.net/articles/JsonPath/)
        to apply to resulting JSON before encoding as XML
        in case full JSON is not a valid XML (or just to simplify xpath expression)

    ### Returns:
    JSON response encoded as XML under the root "result" field.

    ### Example usage in Sheets:
    - Usage in sheets if you want to query the Chuck Norris jokes API
        for a random dirty joke and get the joke value using an XPath expression:
    ```
    =importxml("https://your-api-address/xml/get?
            url=https://api.icndb.com/jokes/random?limitTo=[explicit]",
            "result/value/joke")
    ```

    - Same example but using JSONPath expression:
    ```
    =importxml("https://your-api-address/xml/get?
            url=https://api.icndb.com/jokes/random?limitTo=[explicit]&jsonpath=value.joke",
            "result")
    ```
    """

    # extract any query params that are not captured by the `url`
    # parameter (e.g. because of `&` splitting
    additional_params = {k: v for k, v in _request.query_params.items()
                         if k not in ['url', 'jsonpath']}

    # get the data
    try:
        response = requests.get(url, params=additional_params)

        if not response.ok:
            raise fastapi.HTTPException(response.status_code, response.text)

        result = response.json()

        if jsonpath:
            result = _try_apply_jsonpath(result, jsonpath)

    except Exception as e:
        result = f'error: {str(e)}'

    # ensure single root
    if isinstance(result, list):
        single_root = {'result': {'items': result}}
    else:
        single_root = {'result': result}

    return xmltodict.unparse(single_root, pretty=True)


def _try_apply_jsonpath(result: Union[dict, list], jsonpath: str) -> Union[dict, list]:
    """ applies jsonpath expression or add the error that resulted from trying """
    try:
        values = [match.value for match in jsonpath_ng.parse(jsonpath).find(result)]
        if len(values) == 1:
            result = values[0]
        elif not len(values):
            raise ValueError(f'match for {jsonpath} not found')
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


@app.get("/datapoint/get", response_class=responses.PlainTextResponse)
def datapoint_get(url: str, jsonpath: str, _request: fastapi.Request) -> str:
    """
    GET any value from any API returning a JSON by extracting the
    value using [JSONPath](https://goessner.net/articles/JsonPath/).
    This allows using [IMPORTDATA](https://support.google.com/docs/answer/3093335)
    in Sheets.

    > Warning: IMPORTDATA is
    [limited to 50 calls per sheet](https://support.google.com/docs/answer/3093335)

    ### Parameters:
    - url: url path with parameters already encoded
    - jsonpath: [jsonpath](https://goessner.net/articles/JsonPath/)
        to extract the value from the returned JSON

    ### Returns:
    Value returned as plain text

    ### Example usage in Sheets:
    - Usage in sheets if you want to query the Chuck Norris jokes API
        for a random dirty joke:
    ```
    =importdata("https://your-api-address/datapoint/get?
                url=https://api.icndb.com/jokes/random?limitTo=[explicit]
                &jsonpath=value.joke")
    ```

    """
    # extract any query params that are not captured by the `url`
    # parameter (e.g. because of `&` splitting
    additional_params = {k: v for k, v in _request.query_params.items()
                         if k not in ['url', 'jsonpath']}

    # get the data
    try:
        response = requests.get(url, params=additional_params)

        if not response.ok:
            raise fastapi.HTTPException(response.status_code, response.text)

        result = response.json()

        # jsonpath
        values = [match.value for match in jsonpath_ng.parse(jsonpath).find(result)]

        if not len(values):
            raise ValueError(f'match for {jsonpath} not found')
        if len(values) > 1:
            raise ValueError(f'more than one match for {jsonpath}')

        return str(values[0])

    except Exception as e:
        return f'error: {str(e)}'


