import logging

from flask import current_app

from udata.tasks import connect, job
from udata.api.signals import on_api_call
from udata.core.dataset.signals import on_dataset_published
from udata.core.reuse.signals import on_reuse_published
from udata.core.followers.signals import on_new_follow

from udata_piwik.client import track, bulk_track
from udata_piwik.models import PiwikTracking
from udata_piwik.settings import PIWIK_BULK as PIWIK_BULK_DEFAULT


log = logging.getLogger(__name__)


@connect(on_api_call, route='low.piwik')
def piwik_track_api(url, **params):
    '''Track an API request into Piwik.'''
    log.debug('Sending to piwik: {url}'.format(url=url))
    if 'user_ip' in params:
        params['cip'] = params.pop('user_ip')
    if current_app.config.get('PIWIK_BULK', PIWIK_BULK_DEFAULT):
        PiwikTracking.objects.create(url=url, kwargs=params)
    else:
        track(url, is_api=True, **params)


@job('piwik-bulk-track-api', route='low.piwik')
def piwik_bulk_track_api(self, max_urls):
    '''
    Submit API calls tracking in bulk.

    This task should be scheduled with the max number of URLs
    to process in the batch as sole argument
    Adjust the couple "scheduling/max URLs" to your needs.
    '''
    log.debug('Submitting API calls in bulk to piwik')
    if not isinstance(max_urls, int):
        max_urls = int(max_urls)
    tracking = PiwikTracking.objects[:max_urls]
    bulk_track(*[(pt.url, pt.date, pt.kwargs) for pt in tracking])
    tracking.delete()


@connect(on_dataset_published, route='low.piwik')
def piwik_track_dataset_published(url, **params):
    '''Track a dataset publication into Piwik.'''
    log.debug('Sending to piwik: {url}'.format(url=url))
    track(url, **params)


@connect(on_reuse_published, route='low.piwik')
def piwik_track_reuse_published(url, **params):
    '''Track a reuse publication into Piwik.'''
    log.debug('Sending to piwik: {url}'.format(url=url))
    track(url, **params)


@connect(on_new_follow, route='low.piwik')
def piwik_track_new_follow(url, **params):
    '''Track a new follow into Piwik.'''
    log.debug('Sending to piwik: {url}'.format(url=url))
    track(url, **params)
