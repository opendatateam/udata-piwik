import urllib

from datetime import datetime

import pytest

from udata.utils import faker
from udata_piwik.client import bulk_track, track

from .conftest import PiwikSettings

pytestmark = pytest.mark.settings.with_args(PiwikSettings)

PIWIK_TRACK_URL = f'{PiwikSettings.PIWIK_SCHEME}://{PiwikSettings.PIWIK_URL}/piwik.php'


def test_track(app, rmock):
    '''
    Use bulk_track w/ default params which should log to PIWIK_ID_FRONT
    '''
    rmock.post(PIWIK_TRACK_URL)
    url = 'http://local.test/' + faker.uri_path()
    track(url)
    assert urllib.parse.quote(url, safe='') in rmock.last_request.text
    assert PiwikSettings.PIWIK_AUTH in rmock.last_request.text
    assert f"idsite={PiwikSettings.PIWIK_ID_FRONT}" in rmock.last_request.text


def test_track_is_api(app, rmock):
    '''
    Use bulk_track w/ is_api=True which should log to PIWIK_ID_API
    '''
    rmock.post(PIWIK_TRACK_URL)
    url = 'http://local.test/' + faker.uri_path()
    track(url, is_api=True)
    assert f"idsite={PiwikSettings.PIWIK_ID_API}" in rmock.last_request.text


def test_bulk_track_not_is_api(app, rmock):
    '''
    Use bulk_track w/ is_api=False which should log to PIWIK_ID_FRONT
    '''
    rmock.post(PIWIK_TRACK_URL)
    urls = [('http://local.test/' + faker.uri_path(), datetime.now(), {}) for _ in range(3)]
    urls.append(('https://local.test/utf8-éèü', datetime.now(), {}))

    bulk_track(*urls, is_api=False)

    assert PiwikSettings.PIWIK_AUTH in rmock.last_request.text
    assert f"idsite={PiwikSettings.PIWIK_ID_FRONT}" in rmock.last_request.text

    for url, _date, _ in urls:
        assert urllib.parse.quote(url, safe='') in rmock.last_request.text
        assert _date.strftime('%s') in rmock.last_request.text


def test_bulk_track_is_api(app, rmock):
    '''
    Use bulk_track w/ default params which should log to PIWIK_ID_API
    '''
    rmock.post(PIWIK_TRACK_URL)
    urls = [('http://local.test/' + faker.uri_path(), datetime.now(), {}) for _ in range(3)]
    urls.append(('https://local.test/utf8-éèü', datetime.now(), {}))

    bulk_track(*urls)

    assert f"idsite={PiwikSettings.PIWIK_ID_API}" in rmock.last_request.text
