import pytest
from fastapi import testclient

from proxy import api


@pytest.fixture(scope='module')
def api_client():
    return testclient.TestClient(api.app)


@pytest.mark.integration
def test_api_basic(api_client):
    pass