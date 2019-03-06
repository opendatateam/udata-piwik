# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from datetime import date, timedelta

from flask import request

from udata import tracking
from udata.api.signals import on_api_call
from udata.core.dataset.signals import on_dataset_published
from udata.core.reuse.signals import on_reuse_published
from udata.core.followers.signals import on_new_follow
from udata.core.user.factories import UserFactory

from udata_piwik import tasks

PREFIX = 'https://data.somewhere.com'
GOAL_NEW_DATASET = 1
GOAL_NEW_REUSE = 2
GOAL_NEW_FOLLOW = 3

pytestmark = pytest.mark.options(plugins=['piwik'],
                                 piwik_goals={
                                     'NEW_DATASET': GOAL_NEW_DATASET,
                                     'NEW_REUSE': GOAL_NEW_REUSE,
                                     'NEW_FOLLOW': GOAL_NEW_FOLLOW,
                                 })


@pytest.fixture
def counter(mocker):
    # Mock counter to speedup test as it is already tested elsewhere
    return mocker.patch('udata_piwik.tasks.counter')
    

@pytest.fixture
def track(mocker):
    # Mock track to speedup test as it is already tested elsewhere
    return mocker.patch('udata_piwik.tasks.track')


def test_piwik_current_metrics(counter):
    tasks.piwik_current_metrics()
    counter.count_for.assert_called_with(date.today())


def test_piwik_yesterday_metrics(counter):
    yesterday = date.today() - timedelta(days=1)
    tasks.piwik_yesterday_metrics()
    counter.count_for.assert_called_with(yesterday)


def test_piwik_track_api(track, app):
    path = '/api/1/some/api'
    user = UserFactory()
    with app.test_request_context(path, base_url=PREFIX):
        tracking.send_signal(on_api_call, request, user)

    track.assert_called_with(PREFIX + path, uid=user.id, user_ip=None)


def test_piwik_track_new_follow(track, app):
    path = '/path/to/dataset'
    user = UserFactory()
    with app.test_request_context(path, base_url=PREFIX):
        tracking.send_signal(on_new_follow, request, user)

    track.assert_called_with(PREFIX + path, uid=user.id, user_ip=None, idgoal=GOAL_NEW_FOLLOW)
