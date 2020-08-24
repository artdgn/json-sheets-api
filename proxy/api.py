import logging
import json
from typing import Union, List, Dict

import fastapi
import jsonpath_ng
import requests
import xmltodict
from starlette import responses

logger = logging.getLogger(__name__)

app = fastapi.FastAPI(title='ImportJSON API for Google Sheets')


@app.get('/', response_class=responses.HTMLResponse)
def health():
    """Just a welcome text"""
    return """
        Welcome!<br>
        <a href="/docs">Docs UI</a>?<br>
        <a href="https://github.com/artdgn/json-sheets-api" target="_blank">GitHub</a>?
        """


@app.get("/xml/get", response_class=responses.PlainTextResponse)
def xml_get(url: str,
            _request: fastapi.Request,
            jsonpath: str = None) -> str:
    """
    GET a JSON from a target API and encode it as XML, optionally extracting
    parts from it using [JSONPath](https://goessner.net/articles/JsonPath/).

    ### Parameters:
    - `url`: url path with parameters already encoded
    - Optional `jsonpath`: [jsonpath expression](https://goessner.net/articles/JsonPath/)
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

    additional_params = _upcaptured_query_params(_request, ['url', 'jsonpath'])

    try:
        response = requests.get(url, params=additional_params)
        result = _response_json(response)
        result = _try_apply_jsonpath(result, jsonpath) if jsonpath else result

    except Exception as e:
        result = f'error: {str(e)}'

    return _to_xml(result)


@app.get("/xml/post", response_class=responses.PlainTextResponse)
def xml_post(url: str,
             body_json: str,
             _request: fastapi.Request,
             jsonpath: str = None,
             ) -> str:
    """
    POST a JSON request to a target API and return the resulting JSON encoded
    as XML, optionally extracting parts from it
    using [JSONPath](https://goessner.net/articles/JsonPath/).

    ### Parameters:
    - `url`: url path with parameters already encoded
    - `body_json`: a JSON to send in the request to the target API
    - Optional `jsonpath`: [jsonpath expression](https://goessner.net/articles/JsonPath/)
        to apply to resulting JSON before encoding as XML
        in case full JSON is not a valid XML (or just to simplify xpath expression)

    ### Returns:
    JSON response encoded as XML under the root "result" field.

    ### Example usage in Sheets:

    > Note: quotes in the JSON body need to be doubled to be escaped in Sheets.

    - Usage in sheets to post a fake POST request and get back the resulting id:
    ```
    =importxml("https://your-api-address/xml/post?
            url=https://jsonplaceholder.typicode.com/posts&body_json={""title"":""bla""}",
            "result/id")
    ```

    - Same example but using JSONPath expression:
    ```
    =importxml("https://your-api-address/xml/post?
            url=https://jsonplaceholder.typicode.com/posts&body_json={""title"":""bla""}
            &jsonpath=id", "result")
    ```
    """

    additional_params = _upcaptured_query_params(
        _request, ['url', 'body_json', 'jsonpath'])

    try:
        json_dict = json.loads(body_json)
        response = requests.post(url, params=additional_params, json=json_dict)
        result = _response_json(response)
        result = _try_apply_jsonpath(result, jsonpath) if jsonpath else result

    except Exception as e:
        result = f'error: {str(e)}'

    return _to_xml(result)


@app.get("/datapoint/get", response_class=responses.PlainTextResponse)
def datapoint_get(url: str, jsonpath: str, _request: fastapi.Request) -> str:
    """
    GET a JSON from a target API and extract a value from it
    using [JSONPath](https://goessner.net/articles/JsonPath/).
    This allows using [IMPORTDATA](https://support.google.com/docs/answer/3093335)
    in Sheets.

    > Warning: IMPORTDATA is
    [limited to 50 calls per sheet](https://support.google.com/docs/answer/3093335)

    ### Parameters:
    - `url`: url path with parameters already encoded
    - `jsonpath`: [jsonpath expression](https://goessner.net/articles/JsonPath/)
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
    additional_params = _upcaptured_query_params(_request, ['url', 'jsonpath'])

    try:
        response = requests.get(url, params=additional_params)
        return _single_datapoint_jsonpath_result(response, jsonpath)

    except Exception as e:
        return f'error: {str(e)}'


@app.get("/datapoint/post", response_class=responses.PlainTextResponse)
def datapoint_post(url: str,
                   body_json:str,
                   jsonpath: str,
                   _request: fastapi.Request,
                   ) -> str:
    """
    POST a JSON request to a target API and extract value from
    the response JSON by using
    [JSONPath](https://goessner.net/articles/JsonPath/).
    This allows using [IMPORTDATA](https://support.google.com/docs/answer/3093335)
    in Sheets.

    > Warning: IMPORTDATA is
    [limited to 50 calls per sheet](https://support.google.com/docs/answer/3093335)

    ### Parameters:
    - `url`: url path with parameters already encoded
    - `body_json`: a JSON to send in the request to the target API
    - `jsonpath`: [jsonpath expression](https://goessner.net/articles/JsonPath/)
        to extract the value from the returned JSON

    ### Returns:
    Value returned as plain text

    ### Example usage in Sheets:

    > Note: quotes in the JSON body need to be doubled to be escaped in Sheets.

    - Usage in sheets to post a fake POST request and get back the resulting id:

    ```
    =importdata("https://your-api-address/datapoint/post?
            url=https://jsonplaceholder.typicode.com/posts&body_json={""title"":""bla""}
            &jsonpath=id")
    ```
    """
    additional_params = _upcaptured_query_params(
        _request, ['url', 'body_json', 'jsonpath'])

    try:
        json_dict = json.loads(body_json)
        response = requests.post(url, params=additional_params, json=json_dict)
        return _single_datapoint_jsonpath_result(response, jsonpath)

    except Exception as e:
        return f'error: {str(e)}'


def _upcaptured_query_params(request: fastapi.Request, expected_args: List[str]
                             ) -> dict:
    """
    Extract any query params that are not captured because of `&` splitting.
    """
    return {k: v for k, v in request.query_params.items()
            if k not in expected_args}


def _response_json(response: requests.Response) -> dict:
    """ Extract the JSON from response or raise an error """
    if not response.ok:
        raise fastapi.HTTPException(response.status_code, response.text)
    return response.json()


def _single_datapoint_jsonpath_result(response: requests.Response, jsonpath: str
                                      ) -> str:
    """
    Checks and extracts a single datapoint from the response according to the jsonpath.
    """
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


def _try_apply_jsonpath(result: Union[dict, list],
                        jsonpath: str
                        ) -> Union[dict, list]:
    """ Applies jsonpath expression or adds the error that results from trying """
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


def _to_xml(result: Union[List, Dict]) -> str:
    """
    Wraps a result in a single root structure
    suitable for XML, and converts to XML
    """
    if isinstance(result, list):
        single_root = {'result': {'items': result}}
    else:
        single_root = {'result': result}

    return xmltodict.unparse(single_root, pretty=True)





