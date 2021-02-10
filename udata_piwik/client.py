import logging
import requests

from simplejson.errors import JSONDecodeError
from datetime import date
from urllib.parse import urlencode

from flask import current_app

from . import settings

# Prevent max headers error by raising the hardcoded limit
try:
    import httplib  # or http.client if you're on Python 3
except ImportError:
    import http.client as httplib
httplib._MAXHEADERS = 10000


log = logging.getLogger(__name__)


def analyze(method, **kwargs):
    """Retrieve JSON stats from PIWIK_ID_FRONT for a given `method` and parameters."""
    is_api = kwargs.pop('is_api', False)
    site_id = current_app.config['PIWIK_ID_API'] if is_api else current_app.config['PIWIK_ID_FRONT']
    base_url = '{0}://{1}/index.php'.format(
        current_app.config.get('PIWIK_SCHEME', settings.PIWIK_SCHEME),
        current_app.config['PIWIK_URL'],
    )
    data = {
        'module': 'API',
        'idSite': site_id,
        'method': method,
        'format': kwargs.pop('format', 'json'),
    }
    if current_app.config['PIWIK_AUTH']:
        data['token_auth'] = current_app.config['PIWIK_AUTH']
    if 'date' in kwargs:
        dt = kwargs.pop('date')
        if isinstance(dt, date):
            dt = dt.isoformat()
        kwargs['date'] = dt
    data.update(kwargs)
    timeout = current_app.config.get('PIWIK_ANALYZE_TIMEOUT',
                                     settings.PIWIK_ANALYZE_TIMEOUT)
    json_result = requests.get(base_url, params=data, timeout=timeout).json()
    if isinstance(json_result, list):
        return json_result
    elif json_result.get('result', None) == 'error':
        raise requests.HTTPError(json_result.get('message', 'Analyze client\'s method failed'))


def track(url, **kwargs):
    """Track a request to a given `url` by issuing a POST against Piwik."""
    is_api = kwargs.pop('is_api', False)
    site_id = current_app.config['PIWIK_ID_API'] if is_api else current_app.config['PIWIK_ID_FRONT']
    base_url = '{0}://{1}/piwik.php'.format(
        current_app.config.get('PIWIK_SCHEME', settings.PIWIK_SCHEME),
        current_app.config['PIWIK_URL'],
    )
    data = {
        'rec': 1,
        'url': url,
        'idsite': site_id,
        'token_auth': current_app.config['PIWIK_AUTH']
    }
    data.update(kwargs)
    timeout = current_app.config.get('PIWIK_TRACK_TIMEOUT',
                                     settings.PIWIK_TRACK_TIMEOUT)
    requests.post(base_url, data=data, timeout=timeout)


def encode_for_bulk(url, dt, kwargs, is_api=True):
    qs = {
        'rec': 1,
        'url': url.encode('utf-8'),
        'cdt': dt.strftime('%s'),
    }
    qs.update(kwargs)
    qs['idsite'] = current_app.config['PIWIK_ID_API'] if is_api else current_app.config['PIWIK_ID_FRONT']
    return '?%s' % urlencode(qs)


def bulk_track(*uris, **kwargs):
    '''
    Track multiple requests in one API call

    Each entry should be a 3-tuple (`url`, `date`, `kwargs`) where:
      - `url` is the request URL as string
      - `date` is the original request date
      - `kwargs` is a `dict` with some extras Piwik parameters

    Entries should be sorted chronologicaly as piwik/matomo expect it.
    The ordering is the caller responsibility to avoid double sorting.
    '''
    base_url = '{0}://{1}/piwik.php'.format(
        current_app.config.get('PIWIK_SCHEME', settings.PIWIK_SCHEME),
        current_app.config['PIWIK_URL'],
    )
    is_api = kwargs.pop('is_api', True)
    data = {
        'token_auth': current_app.config['PIWIK_AUTH'],
        'requests': [
            encode_for_bulk(url, ts, _kwargs, is_api=is_api)
            for url, ts, _kwargs in uris
        ]
    }
    timeout = current_app.config.get('PIWIK_TRACK_TIMEOUT',
                                     settings.PIWIK_TRACK_TIMEOUT)
    resp = requests.post(base_url, json=data, timeout=timeout)
    resp.raise_for_status()
    try:
        return resp.json()
    # sometimes we don't have a JSON response from Matomo (eg QueuedTracking)
    except JSONDecodeError:
        return {}
