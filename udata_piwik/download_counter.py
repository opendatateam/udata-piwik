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

    def count(self):
        self.count_downloads()

    def count_downloads(self):
        params = {
            'period': 'day',
            'date': self.day,
            'expanded': 1
        }
        for row in analyze('Actions.getDownloads', **params):
            self.handle_downloads(row)
        for row in analyze('Actions.getOutlinks', **params):
            self.handle_downloads(row)

    def get_downloaded_object(self, hashed_url, resource_id=None):
        if resource_id:
            try:
                data = Dataset.objects.get(resources__id=resource_id)
                resource = get_by(data.resources, 'id', uuid.UUID(resource_id))
            except Dataset.DoesNotExist:
                try:
                    data = CommunityResource.objects.get(id=resource_id)
                    resource = data
                except CommunityResource.DoesNotExist:
                    raise Exception('No object found for resource_id %s' %
                                    resource_id)
        else:
            try:
                data = Dataset.objects.get(resources__urlhash=hashed_url)
                resource = get_by(data.resources, 'urlhash', hashed_url)
            except Dataset.DoesNotExist:
                try:
                    data = CommunityResource.objects.get(urlhash=hashed_url)
                    resource = data
                except CommunityResource.DoesNotExist:
                    raise Exception('No object found for urlhash %s' %
                                    hashed_url)

        return data, resource

    def handle_download(self, data, resource, row):
        if isinstance(data, Dataset):
            dataset = data
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
        elif isinstance(data, CommunityResource):
            log.debug('Found community resource download: %s',
                      resource.url)
            upsert_metric_for_day(resource, self.day, row)
            metric = CommunityResourceViews(resource)
            metric.compute()
            resource.metrics[metric.name] = metric.value
            resource.save()

    def handle_downloads(self, row):
        if 'url' in row:
            try:
                hashed_url = hash_url(row['url'])
                last_url_match = re.match(LATEST_URL_REGEX, row['url'])
                resource_id = last_url_match and last_url_match.group(1)
                data, resource = self.get_downloaded_object(
                    hashed_url, resource_id=resource_id)
                self.handle_download(data, resource, row)
            except Exception:
                log.exception('Unable to count download for %s', row['url'])
        if 'subtable' in row:
            for subrow in row['subtable']:
                self.handle_downloads(subrow)
