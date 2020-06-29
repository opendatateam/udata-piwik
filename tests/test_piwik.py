import pytest

from datetime import date, datetime, timedelta

from udata import frontend, settings
from udata.app import create_app
from udata.core.dataset.factories import (
    DatasetFactory, ResourceFactory, CommunityResourceFactory
)
from udata.core.organization.factories import OrganizationFactory
from udata.core.post.factories import PostFactory
from udata.core.reuse.factories import ReuseFactory
from udata.core.user.factories import UserFactory

from udata.tests.plugin import drop_db

from udata_metrics.client import metrics_client_factory

from udata_piwik.counter import counter
from udata_piwik.upsert import upsert_metric_for_resource
from udata_piwik.metrics import update_resources_metrics_from_backend, update_datasets_metrics_from_backend, update_community_resources_metrics_from_backend

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
    upsert_metric_for_resource(resource, dataset, day, data)
    day = datetime.now() - timedelta(days=2)
    data = {'nb_uniq_visitors': 10, 'nb_hits': 10, 'nb_visits': 10}
    upsert_metric_for_resource(resource, dataset, day, data)
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
    # count twice to ensure idempotence on one day
    counter.count_for(date.today())
    dataset, resource = dataset_resource
    d_w_previous_data, r_w_previous_data = dataset_resource_w_previous_data
    return {
        'app': app,
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


def test_dataset_metric(fixtures):
    metrics_client = metrics_client_factory()
    result = metrics_client.sum_views_from_specific_model('dataset', 'dataset', fixtures['dataset'].id)
    values = next(result.get_points())

    assert values['sum_nb_hits'] == 2
    assert values['sum_nb_uniq_visitors'] == 1
    assert values['sum_nb_visits'] == 1

    update_datasets_metrics_from_backend()
    fixtures['dataset'].reload()
    assert fixtures['dataset'].get_metrics()['views'] == 1


def test_resource_metric(fixtures):
    metrics_client = metrics_client_factory()
    result = metrics_client.sum_views_from_specific_model('resource', 'resource', fixtures['resource'].id)

    values = next(result.get_points())
    # 1 hit on permalink, 1 on url
    assert values['sum_nb_hits'] == 2
    assert values['sum_nb_uniq_visitors'] == 2
    assert values['sum_nb_visits'] == 2

    update_resources_metrics_from_backend()
    fixtures['dataset'].reload()
    resource = fixtures['dataset'].resources[0]
    assert resource.get_metrics()['views'] == 2


def test_resource_metric_with_previous_data(fixtures):
    update_datasets_metrics_from_backend()
    update_resources_metrics_from_backend()
    fixtures['dataset_w_previous_data'].reload()
    resource = fixtures['dataset_w_previous_data'].resources[0]
    assert resource.get_metrics()['views'] == 17


def test_community_resource_metric(fixtures):
    metrics_client = metrics_client_factory()
    result = metrics_client.sum_views_from_specific_model(
        collection='community_resource',
        tag='communityresource',
        model_id=fixtures['community_resource'].id)

    values = next(result.get_points())
    assert values['sum_nb_hits'] == 2
    assert values['sum_nb_uniq_visitors'] == 2
    assert values['sum_nb_visits'] == 2
    
    update_community_resources_metrics_from_backend()
    fixtures['community_resource'].reload()
    assert fixtures['community_resource'].get_metrics()['views'] == 2


def test_two_datasets_one_resource_url(fixtures):
    (d1, d2), (r1, r2) = fixtures['two_datasets_one_resource_url']

    metrics_client = metrics_client_factory()

    result_r1 = metrics_client.sum_views_from_specific_model(
        collection='resource',
        tag='resource',
        model_id=r1.id)
    values_r1 = next(result_r1.get_points())

    result_r2 = metrics_client.sum_views_from_specific_model(
        collection='resource',
        tag='resource',
        model_id=r2.id)
    values_r2 = next(result_r2.get_points())

    assert values_r1['sum_nb_hits'] == 1
    assert values_r1['sum_nb_uniq_visitors'] == 1
    assert values_r1['sum_nb_visits'] == 1

    assert values_r2['sum_nb_hits'] == 2
    assert values_r2['sum_nb_uniq_visitors'] == 2
    assert values_r2['sum_nb_visits'] == 2
