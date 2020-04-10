import logging

from werkzeug.exceptions import NotFound

from udata.models import User, Organization, Reuse, Dataset

from udata_piwik.client import analyze
from udata_piwik.download_counter import DailyDownloadCounter
from udata_piwik.upsert import (
    upsert_metric_for_dataset, upsert_metric_for_reuse,
    upsert_metric_for_organization, upsert_metric_for_user,
)
from udata_piwik.utils import route_from, RouteNotFound

log = logging.getLogger(__name__)


class Counter(object):
    '''Handle view count and delegate download count to DailyDownloadCounter'''
    def __init__(self):
        self.routes = {}

    def route(self, endpoint):
        def wrapper(func):
            self.routes[endpoint] = func
            return func
        return wrapper

    def count_for(self, day):
        log.debug('Counting views...')
        self.count_views(day)
        log.debug('Counting downloads...')
        dl_counter = DailyDownloadCounter(day)
        dl_counter.count()

    def count_views(self, day):
        params = {
            'period': 'day',
            'date': day,
            'expanded': 1
        }
        for row in analyze('Actions.getPageUrls', **params):
            log.debug('Got views data...')
            self.handle_views(row, day)

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
            except Exception:
                log.exception('Unable to count page views for %s', row['url'])
        if 'subtable' in row:
            for subrow in row['subtable']:
                self.handle_views(subrow, day)


counter = Counter()


@counter.route('datasets.show')
def on_dataset_display(data, day, dataset, **kwargs):
    if isinstance(dataset, Dataset):
        upsert_metric_for_dataset(dataset, day, data)


@counter.route('reuses.show')
def on_reuse_display(data, day, reuse, **kwargs):
    if isinstance(reuse, Reuse):
        upsert_metric_for_reuse(reuse, day, data)


@counter.route('organizations.show')
def on_org_display(data, day, org, **kwargs):
    if isinstance(org, Organization):
        upsert_metric_for_organization(org, day, data)


@counter.route('users.show')
def on_user_display(data, day, user, **kwargs):
    if isinstance(user, User):
        upsert_metric_for_user(user, day, data)
