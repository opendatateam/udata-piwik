# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from datetime import date, timedelta

from flask import current_app

from udata.tasks import connect, job
from udata.api.signals import on_api_call
from udata.core.dataset.signals import on_dataset_published
from udata.core.reuse.signals import on_reuse_published
from udata.core.followers.signals import on_new_follow

from .client import track
from .counter import counter


log = logging.getLogger(__name__)


@job('piwik-current-metrics')
def piwik_current_metrics(self):
    '''Fetch piwik metrics for the current day'''
    day = date.today()

    self.log.info('Loading Piwik metrics for today ({day})'.format(day=day))

    counter.count_for(day)


@job('piwik-yesterday-metrics')
def piwik_yesterday_metrics(self):
    '''Bump piwik daily metrics for yesterday'''
    day = date.today() - timedelta(days=1)

    self.log.info('Bump Piwik metrics for {day}'.format(day=day))

    counter.count_for(day)


@connect(on_api_call)
def piwik_track_api(url, **params):
    '''Track an API request into Piwik.'''
    log.debug('Sending to piwik: {url}'.format(url=url))
    track(url, **params)


@connect(on_dataset_published)
def piwik_track_dataset_published(url, **params):
    '''Track a dataset publication into Piwik.'''
    log.debug('Sending to piwik: {url}'.format(url=url))
    goals = current_app.config.get('PIWIK_GOALS')
    if goals:
        params.update({
            'idgoal': goals['NEW_DATASET'],
        })
    track(url, **params)


@connect(on_reuse_published)
def piwik_track_reuse_published(url, **params):
    '''Track a reuse publication into Piwik.'''
    log.debug('Sending to piwik: {url}'.format(url=url))
    goals = current_app.config.get('PIWIK_GOALS')
    if goals:
        params.update({
            'idgoal': goals['NEW_REUSE'],
        })
    track(url, **params)


@connect(on_new_follow)
def piwik_track_new_follow(url, **params):
    '''Track a new follow into Piwik.'''
    log.debug('Sending to piwik: {url}'.format(url=url))
    goals = current_app.config.get('PIWIK_GOALS')
    if goals:
        params.update({
            'idgoal': goals['NEW_FOLLOW'],
        })
    track(url, **params)
