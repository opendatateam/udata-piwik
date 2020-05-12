import logging
import re
import uuid

from udata.models import Dataset, CommunityResource
from udata.utils import hash_url, get_by

from udata_piwik.client import analyze
from udata_piwik.upsert import upsert_metric_for_resource, upsert_metric_for_community_resource

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
        log.debug('Populate rows...')
        self.populate_rows()
        log.debug('Detect download objects...')
        self.detect_download_objects()
        log.debug('Handle resources downloads...')
        self.handle_resources_downloads()
        log.debug('Handle community resource downloads...')
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
        log.debug('Getting downloads data...')
        self.get_rows(analyze('Actions.getDownloads', **params))
        log.debug('Getting outlinks data...')
        self.get_rows(analyze('Actions.getOutlinks', **params))

    def detect_by_resource_id(self, resource_id, row):
        try:
            # use filter().first() to avoid double matches errors
            dataset = Dataset.objects.filter(resources__id=resource_id).first()
            if not dataset:
                raise Dataset.DoesNotExist
            resource = get_by(dataset.resources, 'id', uuid.UUID(resource_id))
            self.resources.append({
                'dataset': dataset,
                'resource': resource,
                'data': row,
                'latest': True,
            })
        except Dataset.DoesNotExist:
            try:
                resource = CommunityResource.objects.get(id=resource_id)
                self.community_resources.append({
                    'resource': resource,
                    'data': row,
                    'latest': True,
                })
            except CommunityResource.DoesNotExist:
                log.error('No object found for resource_id %s' % resource_id)

    def detect_by_url(self, row):
        url = row['url']
        hashed_url = hash_url(url)
        found = False
        datasets = Dataset.objects.filter(resources__urlhash=hashed_url)
        for dataset in datasets:
            resource = get_by(dataset.resources, 'urlhash', hashed_url)
            self.resources.append({
                'dataset': dataset,
                'resource': resource,
                'data': row,
            })
            found = True
        resources = CommunityResource.objects.filter(urlhash=hashed_url)
        for resource in resources:
            self.community_resources.append({
                'resource': resource,
                'data': row,
            })
            found = True
        if not found:
            log.error('No resource found by url', extra={
                'hashed_url': hashed_url,
                'url': url
            })

    def detect_download_objects(self):
        for row in self.rows:
            if 'url' not in row:
                continue
            last_url_match = re.match(LATEST_URL_REGEX, row['url'])
            resource_id = last_url_match and last_url_match.group(1)
            if resource_id:
                self.detect_by_resource_id(resource_id, row)
            else:
                self.detect_by_url(row)

    def handle_resources_downloads(self):
        for item in self.resources:
            row = item['data']
            dataset = item['dataset']
            resource = item['resource']
            latest = item.get('latest', False)
            log.debug('Found resource download: %s', resource.url)
            upsert_metric_for_resource(resource, dataset, self.day, row, latest)

    def handle_community_resources_downloads(self):
        for item in self.community_resources:
            row = item['data']
            resource = item['resource']
            latest = item.get('latest', False)
            log.debug('Found community resource download: %s',
                      resource.url)
            upsert_metric_for_community_resource(resource, resource.dataset, self.day, row, latest)
