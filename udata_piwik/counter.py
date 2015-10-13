# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from datetime import date

from flask import _app_ctx_stack

from werkzeug.exceptions import NotFound
from werkzeug.routing import RequestRedirect
from werkzeug.urls import url_parse

from udata.core.metrics.models import Metrics
from udata.models import (
    db, User, Organization, Reuse, Dataset, CommunityResource
)
from udata.utils import hash_url, get_by

from .client import analyze
from .metrics import (
    DatasetViews, ResourceViews, ReuseViews, OrganizationViews, UserViews,
    OrgDatasetsViews, OrgResourcesDownloads, OrgReusesViews,
    CommunityResourceViews,
    aggregate_datasets_daily, aggregate_reuses_daily
)


log = logging.getLogger(__name__)


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

    try:
        url_adapter.path_info = url_adapter.path_info or parsed_url.path
        url_adapter.query_args = url_adapter.query_args or parsed_url.decode_query()
        return url_adapter.match(parsed_url.path, method)
    except RequestRedirect as re:
        return route_from(re.new_url, method)


_routes = {}

KEYS = 'nb_uniq_visitors nb_hits nb_visits'.split()


def is_today(day):
    today = date.today()
    if isinstance(day, basestring):
        return day == today.isoformat()
    else:
        return day == today


class Counter(object):
    '''Perform reverse rooting and count for daily stats'''
    def __init__(self):
        self.routes = {}

    def route(self, endpoint):
        def wrapper(func):
            self.routes[endpoint] = func
            return func
        return wrapper

    def clear(self, day):
        if not isinstance(day, basestring):
            day = (day or date.today()).isoformat()

        if is_today(day):
            commands = dict(('set__metrics__{0}'.format(k), 0) for k in KEYS)
            for model in Organization, Reuse, User:
                try:
                    model.objects.update(**commands)
                except:
                    log.exception('Unable to clean %s', model.__name__)
            for dataset in Dataset.objects:
                dcommands = commands.copy()
                for i, _ in enumerate(dataset.resources):
                    dcommands.update({
                        'set__resources__{0}__metrics__{1}'.format(i, k): 0
                        for k in KEYS
                    })
                try:
                    dataset.update(**dcommands)
                except:
                    log.exception('Unable to clear dataset %s', dataset.id)

        commands = dict(('unset__values__{0}'.format(k), '1') for k in KEYS)
        metrics = Metrics.objects(level='daily', date=day)
        return metrics.update(upsert=False, **commands)

    def count(self, obj, day, data):
        oid = obj.id if hasattr(obj, 'id') else obj
        if not isinstance(day, basestring):
            day = (day or date.today()).isoformat()

        if hasattr(obj, 'metrics') and day == date.today().isoformat():
            # Update object current metrics
            for k in KEYS:
                obj.metrics[k] = data[k]

        commands = dict(('inc__values__{0}'.format(k), data[k]) for k in KEYS)
        metrics = Metrics.objects(object_id=oid, level='daily', date=day)
        return metrics.update_one(upsert=True, **commands)

    def count_for(self, day):
        self.clear(day)
        self.count_views(day)
        self.count_downloads(day)

    def count_views(self, day):
        params = {
            'period': 'day',
            'date': day,
            'expanded': 1
        }
        for row in analyze('Actions.getPageUrls', **params):
            self.handle_views(row, day)

    def count_downloads(self, day):
        params = {
            'period': 'day',
            'date': day,
            'expanded': 1
        }
        for row in analyze('Actions.getDownloads', **params):
            self.handle_downloads(row, day)
        for row in analyze('Actions.getOutlinks', **params):
            self.handle_downloads(row, day)

    def handle_views(self, row, day):
        if 'url' in row:
            try:
                endpoint, kwargs = route_from(row['url'])
                if endpoint in self.routes:
                    log.debug('Found matching route %s for %s',
                              endpoint, row['url'])
                    handler = self.routes[endpoint]
                    handler(row, day, **kwargs)
            except (NotFound, RouteNotFound):
                pass
            except:
                log.exception('Unable to count page views for %s', row['url'])
        if 'subtable' in row:
            for subrow in row['subtable']:
                self.handle_views(subrow, day)

    def handle_downloads(self, row, day):
        if 'url' in row:
            try:
                hashed_url = hash_url(row['url'])
                data = (
                    Dataset.objects(resources__urlhash=hashed_url).first()
                    or
                    CommunityResource.objects(urlhash=hashed_url).first()
                )
                if isinstance(data, Dataset):
                    dataset = data
                    resource = get_by(dataset.resources, 'urlhash', hashed_url)
                    log.debug('Found resource download: %s', resource.url)
                    self.count(resource, day, row)
                    metric = ResourceViews(resource)
                    metric.compute()
                    # Use the MongoDB positionnal operator ($)
                    cmd = 'set__resources__S__metrics__{0}'.format(metric.name)
                    qs = Dataset.objects(id=dataset.id,
                                         resources__id=resource.id)
                    qs.update(**{cmd: metric.value})
                    if dataset.organization:
                        OrgResourcesDownloads(dataset.organization).compute()
                elif isinstance(data, CommunityResource):
                    resource = data
                    log.debug('Found community resource download: %s',
                              resource.url)
                    self.count(resource, day, row)
                    metric = CommunityResourceViews(resource)
                    metric.compute()
                    resource.metrics[metric.name] = metric.value
                    resource.save()

            except:
                log.exception('Unable to count download for %s', row['url'])
        if 'subtable' in row:
            for subrow in row['subtable']:
                self.handle_downloads(subrow, day)


counter = Counter()


@counter.route('datasets.show')
def on_dataset_display(data, day, dataset, **kwargs):
    if isinstance(dataset, Dataset):
        counter.count(dataset, day, data)
        if is_today(day):
            try:
                dataset.save()
            except:
                log.exception('Unable to save dataset %s', dataset.id)
        DatasetViews(dataset).compute()
        if dataset.organization:
            OrgDatasetsViews(dataset.organization).compute()
            aggregate_datasets_daily(dataset.organization, day)


@counter.route('reuses.show')
def on_reuse_display(data, day, reuse, **kwargs):
    if isinstance(reuse, Reuse):
        counter.count(reuse, day, data)
        if is_today(day):
            try:
                reuse.save()
            except:
                log.exception('Unable to save reuse %s', reuse.id)
        ReuseViews(reuse).compute()
        if reuse.organization:
            OrgReusesViews(reuse.organization).compute()
            aggregate_reuses_daily(reuse.organization, day)


@counter.route('organizations.show')
def on_org_display(data, day, org, **kwargs):
    if isinstance(org, Organization):
        counter.count(org, day, data)
        if is_today(day):
            try:
                org.save()
            except:
                log.exception('Unable to save organization %s', org.id)
        OrganizationViews(org).compute()


@counter.route('users.show')
def on_user_display(data, day, user, **kwargs):
    if isinstance(user, User):
        counter.count(user, day, data)
        if is_today(day):
            try:
                user.save()
            except:
                log.exception('Unable to save user %s', user.id)
        UserViews(user).compute()
