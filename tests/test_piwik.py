# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from datetime import date, datetime, timedelta

from udata import frontend, settings
from udata.app import create_app
from udata.core.metrics.models import Metrics
from udata.core.dataset.factories import (
    DatasetFactory, ResourceFactory, CommunityResourceFactory
)
from udata.core.organization.factories import OrganizationFactory
from udata.core.post.factories import PostFactory
from udata.core.reuse.factories import ReuseFactory
from udata.core.user.factories import UserFactory

from udata.tests.plugin import drop_db

from udata_piwik.counter import counter
from udata_piwik.metrics import upsert_metric_for_day

from .conftest import PiwikSettings
from .client import visit, has_data, reset, download


MODULES = ['core.dataset', 'core.organization', 'core.user', 'core.reuse',
           'core.post']


@pytest.fixture(scope='module')  # noqa
def app(request):
    app = create_app(settings.Defaults, override=PiwikSettings)
    with app.app_context():
        drop_db(app)
    frontend.init_app(app, MODULES)
    with app.app_context():
        yield app
        drop_db(app)


@pytest.fixture(scope='module')
def dataset_resource(app):
    resource = ResourceFactory(url='http://schéma.org')
    dataset = DatasetFactory(resources=[resource])
    # 2x visit
    visit(dataset)
    visit(dataset)
    # 1 download on url, 1 on latest url
    download(resource)
    download(resource, latest=True)
    return dataset, resource


@pytest.fixture(scope='module')
def dataset_resource_w_previous_data(app):
    resource = ResourceFactory()
    dataset = DatasetFactory(resources=[resource])
    day = datetime.now() - timedelta(days=1)
    data = {'nb_uniq_visitors': 5, 'nb_hits': 5, 'nb_visits': 5}
    upsert_metric_for_day(resource, day, data)
    day = datetime.now() - timedelta(days=2)
    data = {'nb_uniq_visitors': 10, 'nb_hits': 10, 'nb_visits': 10}
    upsert_metric_for_day(resource, day, data)
    visit(dataset)
    download(resource)
    download(resource, latest=True)
    return dataset, resource


@pytest.fixture(scope='module')
def two_datasets_one_resource_url(app):
    resource_1 = ResourceFactory(url='http://udata.world')
    resource_2 = ResourceFactory(url='http://udata.world')
    dataset_1 = DatasetFactory(resources=[resource_1])
    dataset_2 = DatasetFactory(resources=[resource_2])
    download(resource_1)
    download(resource_2, latest=True)
    return (dataset_1, dataset_2), (resource_1, resource_2)


@pytest.fixture(scope='module')
def organization(app):
    organization = OrganizationFactory()
    visit(organization)
    return organization


@pytest.fixture(scope='module')
def post(app):
    post = PostFactory()
    visit(post)
    return post


@pytest.fixture(scope='module')
def reuse(app):
    reuse = ReuseFactory()
    visit(reuse)
    return reuse


@pytest.fixture(scope='module')
def user(app):
    user = UserFactory()
    visit(user)
    return user


@pytest.fixture(scope='module')
def community_resource(app):
    community_resource = CommunityResourceFactory()
    download(community_resource)
    download(community_resource, latest=True)
    return community_resource


@pytest.fixture(scope='module')
def reset_piwik():
    reset()


@pytest.fixture(scope='module')
def fixtures(app, reset_piwik, dataset_resource, organization,
             user, reuse, post, community_resource,
             two_datasets_one_resource_url, dataset_resource_w_previous_data):
    # wait for Piwik to be populated
    assert has_data()
    counter.count_for(date.today())
    # count twice to be ensure idempotence on one day
    counter.count_for(date.today())
    dataset, resource = dataset_resource
    d_w_previous_data, r_w_previous_data = dataset_resource_w_previous_data
    return {
        'dataset': dataset,
        'organization': organization,
        'resource': resource,
        'user': user,
        'reuse': reuse,
        'post': post,
        'community_resource': community_resource,
        'two_datasets_one_resource_url': two_datasets_one_resource_url,
        'dataset_w_previous_data': d_w_previous_data,
        'resource_w_previous_data': r_w_previous_data,
    }


def test_objects_have_metrics(fixtures):
    # XXX is this list exhaustive?
    metrics_dataset = Metrics.objects.get_for(fixtures['dataset'])
    assert len(metrics_dataset) == 1
    metrics_org = Metrics.objects.get_for(fixtures['organization'])
    assert len(metrics_org) == 1
    metrics_user = Metrics.objects.get_for(fixtures['user'])
    assert len(metrics_user) == 1
    metrics_reuse = Metrics.objects.get_for(fixtures['reuse'])
    assert len(metrics_reuse) == 1
    metrics_resource = Metrics.objects.get_for(fixtures['resource'])
    assert len(metrics_resource) == 1
    metrics_comres = Metrics.objects.get_for(fixtures['community_resource'])
    assert len(metrics_comres) == 1


def test_dataset_metric(fixtures):
    metrics_dataset = Metrics.objects.get_for(fixtures['dataset'])
    metric = metrics_dataset[0]
    assert metric.level == 'daily'
    assert metric.date == date.today().isoformat()
    assert metric.values == {'nb_hits': 2, 'nb_uniq_visitors': 1,
        'nb_visits': 1}
    fixtures['dataset'].reload()
    assert fixtures['dataset'].metrics['views'] == 1


def test_resource_metric(fixtures):
    metrics_resource = Metrics.objects.get_for(fixtures['resource'])
    metric = metrics_resource[0]
    assert metric.level == 'daily'
    assert metric.date == date.today().isoformat()
    # 1 hit on permalink, 1 on url
    assert metric.values == {'nb_hits': 2, 'nb_uniq_visitors': 2,
        'nb_visits': 2}
    fixtures['dataset'].reload()
    resource = fixtures['dataset'].resources[0]
    assert resource.metrics == {'views': 2}


def test_resource_metric_with_previous_data(fixtures):
    fixtures['dataset_w_previous_data'].reload()
    resource = fixtures['dataset_w_previous_data'].resources[0]
    assert resource.metrics == {'views': 17}


def test_community_resource_metric(fixtures):
    metrics_resource = Metrics.objects.get_for(fixtures['community_resource'])
    metric = metrics_resource[0]
    assert metric.level == 'daily'
    assert metric.date == date.today().isoformat()
    # 1 hit on permalink, 1 on url
    assert metric.values == {'nb_hits': 2, 'nb_uniq_visitors': 2,
        'nb_visits': 2}
    fixtures['community_resource'].reload()
    assert fixtures['community_resource'].metrics['views'] == 2


def test_two_datasets_one_resource_url(fixtures):
    (d1, d2), (r1, r2) = fixtures['two_datasets_one_resource_url']
    metrics_r1 = Metrics.objects.get_for(r1)
    assert len(metrics_r1) == 1
    metrics_r2 = Metrics.objects.get_for(r2)
    assert len(metrics_r2) == 1
    # hit once by resource_1 hashed_url, never by resource_2 latest url rid
    assert metrics_r1[0].values == {'nb_hits': 1, 'nb_uniq_visitors': 1,
        'nb_visits': 1}
    # hit once by resource_1 hashed_url and once by latest url resource id
    # ideally this should be only one but impossible to tell
    assert metrics_r2[0].values == {'nb_hits': 2, 'nb_uniq_visitors': 2,
        'nb_visits': 2}
