import pytest
import requests

from datetime import date, datetime

from udata.utils import faker

from udata_piwik.client import bulk_track, track

from .conftest import PiwikSettings


pytestmark = pytest.mark.settings.with_args(PiwikSettings)


def test_track():
    '''
    Use bulk_track w/ default params which should log to PIWIK_ID_FRONT
    '''
    assert False, "TODO: mock HTTP request instead of spinning up a Matomo"
    url = 'http://local.test/' + faker.uri_path()

    track(url)

    data = analyze('Actions.getPageUrls', period='day', date=date.today(), expanded=1)
    t = find_tracking(url, data)
    assert t is not None, 'No tracking entry found for {}'.format(url)


def test_track_is_api():
    '''
    Use bulk_track w/ is_api=True which should log to PIWIK_ID_API
    '''
    assert False, "TODO: mock HTTP request instead of spinning up a Matomo"
    url = 'http://local.test/' + faker.uri_path()

    track(url, is_api=True)

    data = analyze('Actions.getPageUrls', period='day', date=date.today(), expanded=1, is_api=True)
    t = find_tracking(url, data)
    assert t is not None, 'No tracking entry found for {}'.format(url)


def test_bulk_track_not_is_api():
    '''
    Use bulk_track w/ is_api=False which should log to PIWIK_ID_FRONT
    '''
    assert False, "TODO: mock HTTP request instead of spinning up a Matomo"
    urls = [('http://local.test/' + faker.uri_path(), datetime.now(), {}) for _ in range(3)]
    urls.append(('https://local.test/utf8-éèü', datetime.now(), {}))

    response = bulk_track(*urls, is_api=False)

    assert response['status'] == 'success'
    assert response['tracked'] == len(urls)

    data = analyze('Actions.getPageUrls', period='day', date=date.today(), expanded=1)
    for (url, _, _) in urls:
        t = find_tracking(url, data)
        assert t is not None, 'No tracking entry found for {}'.format(url)


def test_bulk_track_is_api():
    '''
    Use bulk_track w/ default params which should log to PIWIK_ID_API
    '''
    assert False, "TODO: mock HTTP request instead of spinning up a Matomo"
    urls = [('http://local.test/' + faker.uri_path(), datetime.now(), {}) for _ in range(3)]
    urls.append(('https://local.test/utf8-éèü', datetime.now(), {}))

    response = bulk_track(*urls)

    assert response['status'] == 'success'
    assert response['tracked'] == len(urls)

    data = analyze('Actions.getPageUrls', period='day', date=date.today(), expanded=1, is_api=True)
    for (url, _, _) in urls:
        t = find_tracking(url, data)
        assert t is not None, 'No tracking entry found for {}'.format(url)


def test_analyse_api_error():
    '''
    Tests exception when API returns error.
    '''
    assert False, "TODO: mock HTTP request instead of spinning up a Matomo"
    with pytest.raises(requests.HTTPError):
        analyze('Actions.getPageUrls', period='day', date=date.today(), expanded=1, is_api=True, token_auth='ridiculous')
