import pytest
import xmltodict
from fastapi import testclient

from proxy import api


@pytest.fixture(scope='module')
def api_client():
    return testclient.TestClient(api.app)


@pytest.mark.integration
class TestXMLPrice:
    route = 'xml/price'

    def test_xml_price_basic(self, api_client):
        res = api_client.get(f'{self.route}/btc')
        assert res.ok
        data = xmltodict.parse(res.text)

        # test may be flaky, assumes bitcoin didn't go to zero
        assert float(data['result']) > 0

    def test_xml_price_currency(self, api_client):
        default = api_client.get(f'{self.route}/btc')
        in_aud = api_client.get(f'{self.route}/btc?currency=aud')
        price_default = float(xmltodict.parse(default.text)['result'])
        price_aud = float(xmltodict.parse(in_aud.text)['result'])

        # test may be flaky, assumes AUD is worth less than USD
        assert price_aud > price_default

    def test_xml_price_error(self, api_client):
        res = api_client.get(f'{self.route}/bla-bla')
        result = xmltodict.parse(res.text)['result']

        # test may be flaky, assumes there is no "bla-bla" coin
        assert 'not found' in result
