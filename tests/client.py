# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

import requests
from retrying import retry

from udata.core.dataset.models import ResourceMixin

from .settings import PiwikSettings

BASE_URL = 'http://{0.PIWIK_URL}'.format(PiwikSettings)
TRACK_URL = '{0}/piwik.php?idsite={1.PIWIK_ID}&rec=1'.format(BASE_URL,
                                                             PiwikSettings)
RESET_URL = '{0}/reset.php'.format(BASE_URL)


def make_track_request(payload, dt=None):
    dt = dt or datetime.now()
    payload.update({
        'h': dt.hour,
        'm': dt.minute,
        's': dt.second,
    })
    return requests.post(TRACK_URL, data=payload)


@retry(stop_max_attempt_number=20, wait_fixed=500)
def has_data():
    """Has piwik stored somed data?"""
    data = {
        'module': 'API',
        'idSite': PiwikSettings.PIWIK_ID,
        'method': 'Actions.getPageUrls',
        'format': 'json',
        'token_auth': PiwikSettings.PIWIK_AUTH,
        'period': 'day',
        'date': datetime.now().isoformat(),
        'expanded': 1
    }
    r = requests.get('%s/index.php' % BASE_URL, params=data)
    data = r.json()
    print(data)
    assert isinstance(data, list) and len(data)
    return True


def visit(obj):
    if isinstance(obj, ResourceMixin):
        url = obj.url
    else:
        url = obj.external_url
    return make_track_request({'url': url})


def reset():
    res = requests.get(RESET_URL)
    assert 'OK' in res.text
