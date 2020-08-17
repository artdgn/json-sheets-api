import logging

import fastapi
import pandas as pd
from starlette import responses

from proxy.utils import common

common.pandas_options()

logger = logging.getLogger(__name__)

app = fastapi.FastAPI()


@app.get("/csv", response_class=responses.PlainTextResponse)
def csv_stub() -> str:
    return pd.DataFrame([1, 2]).to_csv()
