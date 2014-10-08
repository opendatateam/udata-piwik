# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import sys

from datetime import date, timedelta

from flask import _app_ctx_stack

from werkzeug.urls import url_parse

from udata.models import User, Organization, Reuse, Dataset
from udata.commands import submanager
from udata.core.metrics.models import Metrics

from .client import PiwikClient


log = logging.getLogger(__name__)


m = submanager('piwik',
    help='Piwik related operations',
    description='Handle all Piwik related operations'
)


class RouteNotFound(Exception):
    pass


def route_from(url, method=None):
    appctx = _app_ctx_stack.top
    if appctx is None:
        raise RuntimeError('Attempted to match a URL without the '
                           'application context being pushed. This has to be '
                           'executed when application context is available.')

    url_adapter = appctx.url_adapter
    if url_adapter is None:
        raise RuntimeError('Application was not able to create a URL '
                           'adapter for request independent URL matching. '
                           'You might be able to fix this by setting '
                           'the SERVER_NAME config variable.')
    parsed_url = url_parse(url)
    if parsed_url.netloc is not "" and parsed_url.netloc != url_adapter.server_name:
        raise RouteNotFound
    return url_adapter.match(parsed_url.path, method)


_routes = {}


def route(endpoint):
    def wrapper(func):
        _routes[endpoint] = func
        return func
    return wrapper


def clear(day):
    if not isinstance(day, basestring):
        day = (day or date.today()).isoformat()

    commands = dict(('unset__values__{0}'.format(k), '1') for k in KEYS)
    return Metrics.objects(level='daily', date=day).update(upsert=False, **commands)


def update(obj, day, data):
    oid = obj.id if hasattr(obj, 'id') else obj
    if not isinstance(day, basestring):
        day = (day or date.today()).isoformat()

    commands = dict(('inc__values__{0}'.format(k), data[k]) for k in KEYS)
    return Metrics.objects(object_id=oid, level='daily', date=day).update_one(upsert=True, **commands)


KEYS = 'nb_uniq_visitors nb_hits nb_visits'.split()


@route('datasets.show')
def on_dataset_display(data, day, dataset, **kwargs):
    if isinstance(dataset, Dataset):
        sys.stdout.write('D.')
        update(dataset, day, data)


@route('reuses.show')
def on_reuse_display(data, day, reuse, **kwargs):
    if isinstance(reuse, Reuse):
        sys.stdout.write('R.')
        update(reuse, day, data)


@route('organizations.show')
def on_org_display(data, day, org, **kwargs):
    if isinstance(org, Organization):
        sys.stdout.write('O.')
        update(org, day, data)


@route('users.show')
def on_user_display(data, day, user, **kwargs):
    if isinstance(user, User):
        sys.stdout.write('O.')
        update(user, day, data)


def handle_row(row, day):
    if 'url' in row:
        try:
            endpoint, kwargs = route_from(row['url'])
            if endpoint in _routes:
                handler = _routes[endpoint]
                handler(row, day, **kwargs)
        except:
            pass
    if 'subtable' in row:
        for subrow in row['subtable']:
            handle_row(subrow, day)


def parse_date(string):
    if string:
        parts = [int(s) for s in string.strip().split('-')]
        return date(*parts)


@m.command
def fill(start=None, end=None):
    '''Fill the piwik metrics'''
    api = PiwikClient()

    end = parse_date(end) or date.today()
    start = parse_date(start) or end
    print 'Loading metrics from {start} to {end}'.format(start=start, end=end)

    current_date = start

    while current_date <= end:
        print '--', current_date
        clear(current_date)
        for row in api.get('Actions.getPageUrls', period='day', date='yesterday', expanded=1):
            handle_row(row, current_date)
        current_date += timedelta(days=1)
        print



# from pprint import pprint


# PIWIK_URL_PATTERN = 'http://stats.data.gouv.fr/?module=API&method=Actions.getPageUrl&pageUrl={url}&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous'
# PIWIK_DAILY = 'https://stats.data.gouv.fr/?module=API&method=Actions.getPageUrls&idSite=1&period=day&date=today&format=JSON&token_auth=anonymous&expanded=1'

# Downloads
# https://stats.data.gouv.fr/?module=API&method=Actions.getDownloads&idSite=1&period=day&date=today&format=JSON&token_auth=anonymous&expanded=1
#

# for row in requests.get(PIWIK_DAILY).json():
#     handle_row(row)
