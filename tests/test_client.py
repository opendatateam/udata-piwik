# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from datetime import date, datetime

from udata.utils import faker

from udata_piwik.client import bulk_track, analyze, track

from .conftest import PiwikSettings
from .client import has_data, reset


pytestmark = pytest.mark.settings.with_args(PiwikSettings)


@pytest.fixture()
def reset_piwik():
    reset()


@pytest.fixture()
def ready(app, reset_piwik):
    # wait for Piwik to be populated
    assert has_data()


def find_tracking(url, data):
    for entry in data:
        if entry.get('url') == url:
            return entry
        elif 'subtable' in entry:
            found = find_tracking(url, entry['subtable'])
            if found:
                return found


def test_track(ready):
    url = 'http://local.test/' + faker.uri_path()

    track(url)

    data = analyze('Actions.getPageUrls', period='day', date=date.today(), expanded=1)
    t = find_tracking(url, data)
    assert t is not None, 'No tracking entry found for {}'.format(url)


def test_bulk_track(ready):
    urls = [('http://local.test/' + faker.uri_path(), datetime.now(), {}) for _ in range(3)]
    urls.append(('https://local.test/utf8-éèü', datetime.now(), {}))

    response = bulk_track(*urls)

    assert response['status'] == 'success'
    assert response['tracked'] == len(urls)

    data = analyze('Actions.getPageUrls', period='day', date=date.today(), expanded=1)
    for (url, _, _) in urls:
        t = find_tracking(url, data)
        assert t is not None, 'No tracking entry found for {}'.format(url)
