# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re
import uuid

from udata.models import Dataset, CommunityResource
from udata.utils import hash_url, get_by

from .client import analyze
from .metrics import (
    ResourceViews, OrgResourcesDownloads, CommunityResourceViews,
    upsert_metric_for_day,
)

log = logging.getLogger(__name__)

LATEST_URL_REGEX = 'http[s]?://.*/datasets/r/([0-9a-f-]{36})[/]?$'


class DailyDownloadCounter(object):
    '''Perform reverse routing and count for daily stats'''
    def __init__(self, day):
        self.day = day
        self.rows = []
        self.resources = []
        self.community_resources = []

    def count(self):
        self.populate_rows()
        self.detect_download_objects()
        self.handle_resources_downloads()
        self.handle_community_resources_downloads()

    def get_rows(self, rows):
        for row in rows:
            if 'url' in row:
                self.rows.append(row)
            if 'subtable' in row:
                for subrow in row['subtable']:
                    self.rows.append(subrow)

    def populate_rows(self):
        params = {
            'period': 'day',
            'date': self.day,
            'expanded': 1
        }
        self.get_rows(analyze('Actions.getDownloads', **params))
        self.get_rows(analyze('Actions.getOutlinks', **params))

    def detect_by_resource_id(self, resource_id, row):
        try:
            dataset = Dataset.objects.get(resources__id=resource_id)
            resource = get_by(dataset.resources, 'id', uuid.UUID(resource_id))
            self.resources.append({
                'dataset': dataset,
                'resource': resource,
                'data': row,
            })
        except Dataset.DoesNotExist:
            try:
                resource = CommunityResource.objects.get(id=resource_id)
                self.community_resources.append({
                    'resource': resource,
                    'data': row,
                })
            except CommunityResource.DoesNotExist:
                raise Exception('No object found for resource_id %s' %
                                resource_id)

    def detect_by_hashed_url(self, hashed_url, row):
        found = False
        try:
            datasets = Dataset.objects.filter(resources__urlhash=hashed_url)
            for dataset in datasets:
                resource = get_by(dataset.resources, 'urlhash', hashed_url)
                self.resources.append({
                    'dataset': dataset,
                    'resource': resource,
                    'data': row,
                })
                found = True
        except Dataset.DoesNotExist:
            pass
        try:
            resources = CommunityResource.objects.filter(urlhash=hashed_url)
            for resource in resources:
                self.community_resources.append({
                    'resource': resource,
                    'data': row,
                })
                found = True
        except CommunityResource.DoesNotExist:
            pass
        if not found:
            raise Exception('No object found for urlhash %s' % hashed_url)

    def detect_download_objects(self):
        for row in self.rows:
            last_url_match = re.match(LATEST_URL_REGEX, row['url'])
            resource_id = last_url_match and last_url_match.group(1)
            if resource_id:
                self.detect_by_resource_id(resource_id, row)
            else:
                hashed_url = hash_url(row['url'])
                self.detect_by_hashed_url(hashed_url, row)

    def handle_resources_downloads(self):
        for item in self.resources:
            row = item['data']
            dataset = item['dataset']
            resource = item['resource']
            log.debug('Found resource download: %s', resource.url)
            upsert_metric_for_day(resource, self.day, row)
            metric = ResourceViews(resource)
            metric.compute()
            # Use the MongoDB positionnal operator ($)
            cmd = 'set__resources__S__metrics__{0}'.format(metric.name)
            qs = Dataset.objects(id=dataset.id,
                                 resources__id=resource.id)
            qs.update(**{cmd: metric.value})
            if dataset.organization:
                OrgResourcesDownloads(dataset.organization).compute()

    def handle_community_resources_downloads(self):
        for item in self.community_resources:
            row = item['data']
            resource = item['resource']
            log.debug('Found community resource download: %s',
                      resource.url)
            upsert_metric_for_day(resource, self.day, row)
            metric = CommunityResourceViews(resource)
            metric.compute()
            resource.metrics[metric.name] = metric.value
            resource.save()
