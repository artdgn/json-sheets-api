import logging

import fastapi
from starlette import responses
import xmltodict

logger = logging.getLogger(__name__)

app = fastapi.FastAPI()


@app.get("/xml", response_class=responses.PlainTextResponse)
def xml_stub() -> str:
    d = {'a': 1.2, 'b': {'c': 1}}
    return xmltodict.unparse({'root': d}, pretty=True)

# in sheets: =importxml("https://89c496b5ae3f.ngrok.io/xml","root/a")
