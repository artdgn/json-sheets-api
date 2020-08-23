import pytest
import xmltodict
from fastapi import testclient

from proxy import api


@pytest.fixture(scope='module')
def api_client():
    return testclient.TestClient(api.app)


@pytest.mark.integration
def test_health(api_client):
    res = api_client.get('/')
    assert res.ok
    assert '/docs' in res.text


@pytest.mark.integration
class TestXMLGetJSON:
    route = 'xml/get'

    def test_basic(self, api_client):
        url = 'https://api.icndb.com/jokes/random'
        res = api_client.get(f'{self.route}', params=dict(url=url))
        assert res.ok
        data = xmltodict.parse(res.text)

        # test may be flaky, Chuck Norris doesn't have to be
        # part of a Chuck Norris joke if he doesn't feel like it
        assert 'chuck' in data['result']['value']['joke'].lower()

    @pytest.mark.parametrize('url', [
        'https://jsonplaceholder.typicode.com/',  # url not returning a JSON
        'https://anskjvas/'  # HTTP error
    ])
    def test_json_errors(self, api_client, url):
        res = api_client.get(f'{self.route}', params=dict(url=url))
        assert res.ok
        data = xmltodict.parse(res.text)
        assert 'error' in data['result']

    def test_multiple_params(self, api_client):
        res = api_client.get(
            f'{self.route}',
            params=dict(
                url='https://api.coingecko.com/api/v3/simple/price?'
                    'ids=bitcoin&vs_currencies=aud',
            ))
        data = xmltodict.parse(res.text)
        # vs_currencies parameter was not ignored
        assert data['result']['bitcoin']['aud']

    def test_jsonpath(self, api_client):
        url = 'https://jsonplaceholder.typicode.com/posts/1/comments'
        res = api_client.get(f'{self.route}',
                             params=dict(url=url, jsonpath='[1].email'))
        data = xmltodict.parse(res.text)
        assert '@' in data['result'].lower()

    @pytest.mark.parametrize('url', [
        'https://jsonplaceholder.typicode.com/posts/1',
        'https://jsonplaceholder.typicode.com/posts/1/comments',
    ])
    @pytest.mark.parametrize('jsonpath', [
        '/#$',
        '[10].email'
    ])
    def test_jsonpath_errors(self, api_client, url, jsonpath):
        res = api_client.get(f'{self.route}', params=dict(url=url, jsonpath=jsonpath))
        data = xmltodict.parse(res.text)
        assert data
        assert 'jsonpath-error' in res.text


@pytest.mark.integration
class TestDatapointGet:
    route = 'datapoint/get'

    def test_basic_jsonpath(self, api_client):
        url = 'https://jsonplaceholder.typicode.com/posts/1/comments'
        res = api_client.get(f'{self.route}',
                             params=dict(url=url, jsonpath='[1].email'))
        assert '@' in res.text

    @pytest.mark.parametrize('jsonpath, error_text', [
        ('/#$', 'Unexpected character'),
        ('[10].email', 'not found'),
        ('[*].email', 'more than one'),
    ])
    def test_jsonpath_errors(self, api_client, jsonpath, error_text):
        url = 'https://jsonplaceholder.typicode.com/posts/1/comments'
        res = api_client.get(f'{self.route}', params=dict(url=url, jsonpath=jsonpath))
        assert 'error' in res.text and error_text in res.text
