# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from datetime import date

from udata.core.metrics.models import Metrics
from udata.core.dataset.factories import (
    DatasetFactory, ResourceFactory, CommunityResourceFactory
)
from udata.core.organization.factories import OrganizationFactory
from udata.core.post.factories import PostFactory
from udata.core.reuse.factories import ReuseFactory
from udata.core.user.factories import UserFactory

from udata_piwik.commands import fill

from .client import visit, has_data, reset, download


@pytest.fixture(scope='module')
def dataset_resource():
    resource = ResourceFactory()
    dataset = DatasetFactory(resources=[resource])
    # 2x visit
    visit(dataset)
    visit(dataset)
    download(resource)
    download(resource, latest=True)
    return dataset, resource


@pytest.fixture(scope='module')
def organization():
    organization = OrganizationFactory()
    visit(organization)
    return organization


@pytest.fixture(scope='module')
def post():
    post = PostFactory()
    visit(post)
    return post


@pytest.fixture(scope='module')
def reuse():
    reuse = ReuseFactory()
    visit(reuse)
    return reuse


@pytest.fixture(scope='module')
def user():
    user = UserFactory()
    visit(user)
    return user


@pytest.fixture(scope='module')
def community_resource():
    community_resource = CommunityResourceFactory()
    download(community_resource)
    return community_resource


@pytest.fixture(scope='module')
def reset_piwik():
    reset()


@pytest.fixture(scope='module')
def fixtures(clean_db, reset_piwik, dataset_resource, organization,
             user, reuse, post, community_resource):
    # wait for Piwik to be populated
    assert has_data()
    fill()
    dataset, resource = dataset_resource
    # TODO make this (and fixtures creation) dynamic
    return {
        'dataset': dataset,
        'organization': organization,
        'resource': resource,
        'user': user,
        'reuse': reuse,
        'post': post,
        'community_resource': community_resource,
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


def test_resource_metric(fixtures):
    metrics_resource = Metrics.objects.get_for(fixtures['resource'])
    metric = metrics_resource[0]
    assert metric.level == 'daily'
    assert metric.date == date.today().isoformat()
    # 1 hit on permalink, 1 on url
    assert metric.values == {'nb_hits': 2, 'nb_uniq_visitors': 1,
        'nb_visits': 1}
