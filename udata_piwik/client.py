# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import requests

from datetime import date

from flask import current_app

log = logging.getLogger(__name__)


class PiwikClient(object):
    @property
    def base_url(self):
        return 'http://{0}/index.php'.format(current_app.config['PIWIK_URL'])

    def params(self, method, **kwargs):
        data = {
            'module': 'API',
            'idSite': current_app.config['PIWIK_ID'],
            'method': method,
            'format': kwargs.pop('format', 'json'),
            'token_auth': kwargs.get('token_auth', 'anonymous')
        }
        if 'date' in kwargs:
            dt = kwargs.pop('date')
            if isinstance(dt, date):
                dt = dt.isoformat()
            kwargs['date'] = dt
        data.update(kwargs)
        return data

    def get(self, method, **kwargs):
        r = requests.get(self.base_url, params=self.params(method, **kwargs))
        return r.json()

    def post(self, method, **kwargs):
        r = requests.post(self.base_url, params=self.params(method, **kwargs))
        return r.json()
