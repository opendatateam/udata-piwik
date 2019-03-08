# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import requests

from datetime import date
from urllib import urlencode

from flask import current_app

from . import settings

log = logging.getLogger(__name__)


def analyze(method, **kwargs):
    """Retrieve JSON stats from Piwik for a given `method` and parameters."""
    base_url = '{0}://{1}/index.php'.format(
        current_app.config.get('PIWIK_SCHEME', settings.PIWIK_SCHEME),
        current_app.config['PIWIK_URL'],
    )
    data = {
        'module': 'API',
        'idSite': current_app.config['PIWIK_ID'],
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
    r = requests.get(base_url, params=data, timeout=timeout)
    return r.json()


def track(url, **kwargs):
    """Track a request to a given `url` by issuing a POST against Piwik."""
    base_url = '{0}://{1}/piwik.php'.format(
        current_app.config.get('PIWIK_SCHEME', settings.PIWIK_SCHEME),
        current_app.config['PIWIK_URL'],
    )
    data = {
        'rec': 1,
        'idsite': current_app.config['PIWIK_ID'],
        'url': url,
        'token_auth': current_app.config['PIWIK_AUTH']
    }
    data.update(kwargs)
    timeout = current_app.config.get('PIWIK_TRACK_TIMEOUT',
                                     settings.PIWIK_TRACK_TIMEOUT)
    requests.post(base_url, data=data, timeout=timeout)


def encode_for_bulk(url, dt, kwargs):
    qs = {
        'rec': 1,
        'idsite': current_app.config['PIWIK_ID'],
        'url': url,
        'cdt': dt.strftime('%s'),
    }
    qs.update(kwargs)
    return '?' + urlencode(qs)


def bulk_track(*uris):
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
    data = {
        'token_auth': current_app.config['PIWIK_AUTH'],
        'requests': [
            encode_for_bulk(url, ts, kwargs)
            for url, ts, kwargs in uris
        ]
    }
    timeout = current_app.config.get('PIWIK_TRACK_TIMEOUT',
                                     settings.PIWIK_TRACK_TIMEOUT)
    resp = requests.post(base_url, json=data, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
