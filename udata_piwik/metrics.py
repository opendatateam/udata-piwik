# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from udata.core.metrics import Metric
from udata.core.metrics.models import Metrics
from udata.i18n import lazy_gettext as _

from udata.models import User, Organization, Reuse, Dataset

log = logging.getLogger(__name__)


from . import client


class HitsMetric(Metric):
    name = 'nb_hits'
    display_name = _('Hits')

    def get_value(self):
        pass


class DatasetHits(HitsMetric):
    model = Dataset


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
        return int(Metrics.objects(object_id=self.target.id, level='daily').sum('values.nb_uniq_visitors'))


class DatasetViews(ViewsMetric):
    model = Dataset


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
        ids = [d.id for d in Dataset.objects(organization=self.target).only('id')]
        return int(Metrics.objects(object_id__in=ids, level='daily').sum('values.nb_uniq_visitors'))


class OrgReusesViews(Metric):
    model = Organization
    name = 'reuse_views'
    display_name = _('Reuses views')

    def get_value(self):
        ids = [d.id for d in Reuse.objects(organization=self.target).only('id')]
        return int(Metrics.objects(object_id__in=ids, level='daily').sum('values.nb_uniq_visitors'))
