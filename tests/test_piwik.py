# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from datetime import date

from udata.core.metrics.models import Metrics
from udata.core.dataset.factories import (
    DatasetFactory, ResourceFactory, CommunityResourceFactory
)
from udata.core.organization.factories import OrganizationFactory
from udata_piwik.commands import fill

from .client import visit, has_data, reset


@pytest.fixture(scope='module')
def dataset_resource():
    resource = ResourceFactory(url='http://localhost/resource')
    dataset = DatasetFactory(resources=[resource])
    # 2x visit
    visit(dataset)
    visit(dataset)
    visit(resource)
    return dataset, resource


@pytest.fixture(scope='module')
def community_resource():
    community_resource = CommunityResourceFactory()
    visit(community_resource)
    return community_resource


@pytest.fixture(scope='module')
def organization():
    organization = OrganizationFactory()
    visit(organization)
    return organization


@pytest.fixture(scope='module')
def reset_piwik():
    reset()


@pytest.fixture(scope='module')
def fixtures(clean_db, reset_piwik, dataset_resource, organization,
             community_resource):
    # wait for Piwik to be populated
    assert has_data()
    fill()
    dataset, resource = dataset_resource
    return {
        'dataset': dataset,
        'organization': organization,
        'resource': resource,
        'community_resource': community_resource
    }


def test_objects_have_metrics(fixtures):
    # TODO more objects
    # TODO search 'def external_url' to know which objects are concerned
    metrics_dataset = Metrics.objects.get_for(fixtures['dataset'])
    assert len(metrics_dataset) == 1
    metrics_org = Metrics.objects.get_for(fixtures['organization'])
    assert len(metrics_org) == 1
    # metrics_resource = Metrics.objects.get_for(fixtures['resource'])
    # assert len(metrics_resource) == 1
    # metrics_resource_com = Metrics.objects.get_for(fixtures['resource_com'])
    # assert len(metrics_resource_com) == 1


def test_dataset_metric(fixtures):
    metrics_dataset = Metrics.objects.get_for(fixtures['dataset'])
    metric = metrics_dataset[0]
    assert metric.level == 'daily'
    assert metric.date == date.today().isoformat()
    assert metric.values == {'nb_hits': 2, 'nb_uniq_visitors': 1,
        'nb_visits': 1}


def test_organization_metric(fixtures):
    metrics_org = Metrics.objects.get_for(fixtures['organization'])
    metric = metrics_org[0]
    assert metric.level == 'daily'
    assert metric.date == date.today().isoformat()
    assert metric.values == {'nb_hits': 1, 'nb_uniq_visitors': 1,
        'nb_visits': 1}

# TODO test downloads (resources, community resources, permalink)
