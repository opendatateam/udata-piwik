# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import pytest
import sys
from urlparse import urlparse

from udata import frontend, settings
from udata.app import create_app
from udata.models import db as DB
from udata.settings import Testing

MODULES = ['core.dataset', 'core.organization', 'core.user', 'core.reuse',
           'core.discussions', 'core.post']


class PiwikSettings(Testing):
    PIWIK_ID = 1
    PIWIK_URL = os.environ.get('PIWIK_URL', 'localhost:8080')
    PIWIK_AUTH = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    PIWIK_GOALS = {
        'NEW_DATASET': 1,
        'NEW_REUSE': 2,
        'NEW_FOLLOW': 3,
        'SHARE': 4,
        'RESOURCE_DOWNLOAD': 5,
        'RESOURCE_REDIRECT': 6,
    }


@pytest.fixture(scope='module')  # noqa
def app():
    reload(sys).setdefaultencoding('ascii')
    app = create_app(settings.Defaults, override=PiwikSettings)
    frontend.init_app(app, MODULES)
    return app


def drop_db(app):
    '''Clear the database'''
    parsed_url = urlparse(app.config['MONGODB_HOST'])
    # drop the leading /
    db_name = parsed_url.path[1:]
    DB.connection.drop_database(db_name)


@pytest.fixture(scope='module')
def clean_db(app):
    drop_db(app)
    yield
    with app.app_context():
        drop_db(app)
