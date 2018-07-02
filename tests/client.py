from datetime import datetime

import requests
from retrying import retry

from udata_piwik.client import track

from .conftest import PiwikSettings

BASE_URL = 'http://{0.PIWIK_URL}'.format(PiwikSettings)
RESET_URL = '{0}/reset.php'.format(BASE_URL)


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
    assert isinstance(data, list) and len(data)
    return True


def visit(obj):
    return track(obj.external_url)


def download(obj, context_url=None, latest=False):
    context_url = context_url or obj.url
    url = obj.latest if latest else obj.url
    return track(context_url, download=url)


def reset():
    res = requests.get(RESET_URL)
    assert 'OK' in res.text
