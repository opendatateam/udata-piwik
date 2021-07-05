import pytest

from datetime import date, timedelta

from flask import request

from udata import tracking
from udata.api.signals import on_api_call
from udata.core.followers.signals import on_new_follow
from udata.core.user.factories import UserFactory
from udata.utils import faker

from udata_piwik import tasks
from udata_piwik.factories import PiwikTrackingFactory
from udata_piwik.models import PiwikTracking


PREFIX = 'https://data.somewhere.com'

pytestmark = pytest.mark.options(plugins=['piwik'])


@pytest.fixture
def counter(mocker):
    # Mock counter to speedup test as it is already tested elsewhere
    return mocker.patch('udata_piwik.tasks.counter')


@pytest.fixture
def track(mocker):
    # Mock track to speedup test as it is already tested elsewhere
    return mocker.patch('udata_piwik.tasks.track')


@pytest.fixture
def bulk_track(mocker):
    # Mock track to speedup test as it is already tested elsewhere
    return mocker.patch('udata_piwik.tasks.bulk_track')


def test_piwik_current_metrics(app, counter):
    tasks.piwik_current_metrics()
    counter.count_for.assert_called_with(date.today())


def test_piwik_yesterday_metrics(app, counter):
    yesterday = date.today() - timedelta(days=1)
    tasks.piwik_yesterday_metrics()
    counter.count_for.assert_called_with(yesterday)


@pytest.mark.options(PIWIK_BULK=False)
def test_piwik_track_api_without_bulk(track, app, clean_db):
    path = '/api/1/some/api'
    user = UserFactory()
    ip = faker.ipv4()
    with app.test_request_context(path, base_url=PREFIX,
                                  environ_base={'REMOTE_ADDR': ip}):
        tracking.send_signal(on_api_call, request, user)

    track.assert_called_with(PREFIX + path, uid=user.id, cip=ip, is_api=True)
    assert PiwikTracking.objects.count() == 0


@pytest.mark.options(PIWIK_BULK=True)
def test_piwik_track_api_with_bulk(track, app, clean_db):
    path = '/api/1/some/api'
    user = UserFactory()
    ip = faker.ipv4()
    with app.test_request_context(path, base_url=PREFIX,
                                  environ_base={'REMOTE_ADDR': ip}):
        tracking.send_signal(on_api_call, request, user)

    assert not track.called
    assert PiwikTracking.objects.count() == 1

    pt = PiwikTracking.objects.first()
    assert pt.url == PREFIX + path
    assert pt.date is not None
    assert pt.kwargs == {
        'uid': user.id,
        'cip': ip,
    }


@pytest.mark.options(PIWIK_BULK=True)
def test_piwik_track_api_with_bulk_and_spaces_in_url(track, app, clean_db):
    path = '/api/1/some/api?q=query with spaces&other=with space'
    encoded_path = path.replace(' ', '%20')
    user = UserFactory()
    with app.test_request_context(path, base_url=PREFIX):
        tracking.send_signal(on_api_call, request, user)

    assert not track.called
    assert PiwikTracking.objects.count() == 1

    pt = PiwikTracking.objects.first()
    assert pt.url in (PREFIX + path, PREFIX + encoded_path)


def test_piwik_bulk_track_api(bulk_track, clean_db, mocker):
    max_urls = 2
    total = 3
    entries = PiwikTrackingFactory.create_batch(total)

    tasks.piwik_bulk_track_api(max_urls)

    assert PiwikTracking.objects.count() == total - max_urls
    bulk_track.assert_called_with(*[
        (e.url, mocker.ANY, e.kwargs)
        # Chronological order expected
        for e in sorted(entries, key=lambda e: e.date)[:max_urls]
    ])

    tasks.piwik_bulk_track_api(max_urls)

    assert PiwikTracking.objects.count() == 0
    bulk_track.assert_called_with(*[
        (e.url, mocker.ANY, e.kwargs)
        # Chronological order expected
        for e in sorted(entries, key=lambda e: e.date)[max_urls:]
    ])


def test_piwik_bulk_track_api_with_string_parameter(bulk_track, clean_db, mocker):
    max_urls = 2
    total = 3
    entries = PiwikTrackingFactory.create_batch(total)

    tasks.piwik_bulk_track_api(str(max_urls))

    assert PiwikTracking.objects.count() == total - max_urls
    bulk_track.assert_called_with(*[
        (e.url, mocker.ANY, e.kwargs)
        # Chronoligical order expected
        for e in sorted(entries, key=lambda e: e.date)[:max_urls]
    ])


def test_piwik_track_new_follow(track, app):
    path = '/path/to/dataset'
    user = UserFactory()
    with app.test_request_context(path, base_url=PREFIX):
        tracking.send_signal(on_new_follow, request, user)

    track.assert_called_with(PREFIX + path, uid=user.id, user_ip=None)
