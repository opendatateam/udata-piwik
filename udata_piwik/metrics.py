# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
import logging

from udata.core.metrics import Metric
from udata.core.metrics.models import Metrics
from udata.i18n import lazy_gettext as _

from udata.models import (
    User, Organization, Reuse, Dataset, Resource, CommunityResource
)


log = logging.getLogger(__name__)


class HitsMetric(Metric):
    name = 'nb_hits'
    display_name = _('Hits')

    def get_value(self):
        pass


class DatasetHits(HitsMetric):
    model = Dataset


class ResourceHits(HitsMetric):
    model = Resource


class CommunityResourceHits(HitsMetric):
    model = CommunityResource


class ReuseHits(HitsMetric):
    model = Reuse


class OrganizationHits(HitsMetric):
    model = Organization


class UserHits(HitsMetric):
    model = User


class VisitsMetric(Metric):
    name = 'nb_visits'
    display_name = _('Visits')

    def get_value(self):
        pass


class DatasetVisits(VisitsMetric):
    model = Dataset


class ResourceVisits(VisitsMetric):
    model = Resource


class CommunityResourceVisits(VisitsMetric):
    model = CommunityResource


class ReuseVisits(VisitsMetric):
    model = Reuse


class OrganizationVisits(VisitsMetric):
    model = Organization


class UserVisits(VisitsMetric):
    model = User


class VisitorsMetric(Metric):
    name = 'nb_uniq_visitors'
    display_name = _('Visitors')

    def get_value(self):
        pass


class DatasetVisitors(VisitorsMetric):
    model = Dataset


class ResourceVisitors(VisitorsMetric):
    model = Resource


class CommunityResourceVisitors(VisitorsMetric):
    model = CommunityResource


class ReuseVisitors(VisitorsMetric):
    model = Reuse


class OrganizationVisitors(VisitorsMetric):
    model = Organization


class UserVisitors(VisitorsMetric):
    model = User


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
            [r.id for r in d.resources] for d in
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


KEYS = 'nb_uniq_visitors nb_hits nb_visits'.split()


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
