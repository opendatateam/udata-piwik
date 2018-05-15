# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
import logging

from datetime import date

from udata.core.metrics import Metric
from udata.core.metrics.models import Metrics
from udata.i18n import lazy_gettext as _

from udata.models import (
    User, Organization, Reuse, Dataset, Resource, CommunityResource
)

KEYS = 'nb_uniq_visitors nb_hits nb_visits'.split()


log = logging.getLogger(__name__)


class ViewsMetric(Metric):
    name = 'views'
    display_name = _('Views')

    def get_value(self):
        return int(Metrics.objects(object_id=self.target.id, level='daily')
                          .sum('values.nb_uniq_visitors'))


class DatasetViews(ViewsMetric):
    model = Dataset


class ResourceViews(ViewsMetric):
    model = Resource


class CommunityResourceViews(ViewsMetric):
    model = CommunityResource


class ReuseViews(ViewsMetric):
    model = Reuse


class OrganizationViews(ViewsMetric):
    model = Organization


class UserViews(ViewsMetric):
    model = User


class OrgDatasetsViews(Metric):
    model = Organization
    name = 'dataset_views'
    display_name = _('Datasets views')

    def get_value(self):
        ids = [d.id for d in
               (Dataset.objects(organization=self.target).only('id') or [])]
        return int(Metrics.objects(object_id__in=ids, level='daily')
                          .sum('values.nb_uniq_visitors'))


class OrgResourcesDownloads(Metric):
    model = Organization
    name = 'resource_downloads'
    display_name = _('Resources downloads')

    def get_value(self):
        ids = itertools.chain(*[
            [getattr(r, 'id', None) for r in d.resources or []] for d in
            (Dataset.objects(organization=self.target).only('resources') or [])
        ])
        return int(Metrics.objects(object_id__in=ids, level='daily')
                          .sum('values.nb_uniq_visitors'))


class OrgReusesViews(Metric):
    model = Organization
    name = 'reuse_views'
    display_name = _('Reuses views')

    def get_value(self):
        ids = [d.id for d in
               (Reuse.objects(organization=self.target).only('id') or [])]
        return int(Metrics.objects(object_id__in=ids, level='daily')
                          .sum('values.nb_uniq_visitors'))


def aggregate_datasets_daily(org, day):
    keys = ['datasets_{0}'.format(k) for k in KEYS]
    ids = [d.id for d in Dataset.objects(organization=org).only('id')]
    metrics = Metrics.objects(object_id__in=ids,
                              level='daily', date=day.isoformat())
    values = [int(metrics.sum('values.{0}'.format(k))) for k in KEYS]
    return Metrics.objects.update_daily(org, day, **dict(zip(keys, values)))


def aggregate_reuses_daily(org, day):
    keys = ['reuses_{0}'.format(k) for k in KEYS]
    ids = [r.id for r in Reuse.objects(organization=org).only('id')]
    metrics = Metrics.objects(object_id__in=ids,
                              level='daily', date=day.isoformat())
    values = [int(metrics.sum('values.{0}'.format(k))) for k in KEYS]
    Metrics.objects.update_daily(org, day, **dict(zip(keys, values)))


def upsert_metric_for_day(obj, day, data):
    oid = obj.id if hasattr(obj, 'id') else obj
    if not isinstance(day, basestring):
        day = (day or date.today()).isoformat()
    commands = dict(('inc__values__{0}'.format(k), data[k]) for k in KEYS)
    metrics = Metrics.objects(object_id=oid, level='daily', date=day)
    return metrics.update_one(upsert=True, **commands)


def clear_metrics_for_day(day):
    if not isinstance(day, basestring):
        day = (day or date.today()).isoformat()
    commands = dict(('unset__values__{0}'.format(k), 1) for k in KEYS)
    metrics = Metrics.objects(level='daily', date=day)
    return metrics.update(upsert=False, **commands)
