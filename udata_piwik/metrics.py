import logging
import uuid

from udata_metrics.client import metrics_client_factory

from udata.core.dataset.models import Dataset, get_resource, CommunityResource
from udata.models import Reuse, User, Organization


log = logging.getLogger(__name__)


def update_metrics_from_backend():
    update_datasets_metrics_from_backend()
    update_resources_metrics_from_backend()
    update_community_resources_metrics_from_backend()
    update_reuses_metrics_from_backend()
    update_organizations_metrics_from_backend()
    update_users_metrics_from_backend()


def process_metrics_result(client, result, model):
    model_str = model.__name__.lower()
    for (_, keys), _values in result.items():
        values = next(_values)
        values.pop('time')
        try:
            model_id = keys[model_str]
        except KeyError:
            model_id = keys['user_view']

        specific_result = client.sum_views_from_specific_model(
            collection='community_resource' if model_str == 'communityresource' else model_str,
            tag='user_view' if model_str == 'user' else model_str,
            model_id=model_id)

        specific_values = next(specific_result.get_points())

        model_result = model.objects.filter(id=model_id).first()

        if model_result:
            log.debug(f'Found {model_str} {model_result.id}: {specific_values}')
            model_result.metrics['views'] = specific_values['sum_nb_visits']
            try:
                model_result.save(signal_kwargs={'ignores': ['post_save']})
            except Exception as e:
                log.exception(e)
                continue
        else:
            log.error(f'{model_str} not found', extra={
                'id': model_id
            })


def update_resources_metrics_from_backend():
    '''
    Update resource's metrics from backend.
    Get a sum of all metrics for `resource_views` on the backend and
    attach them to `resource.metrics`.
    '''
    log.info('Updating resources metrics from backend...')
    client = metrics_client_factory()
    result = client.get_previous_day_measurements(collection='resource', tag='resource')
    for (_, keys), _values in result.items():
        values = next(_values)
        values.pop('time')
        resource_id = keys['resource']

        specific_result = client.sum_views_from_specific_model(
            collection='resource',
            tag='resource',
            model_id=resource_id)
        specific_values = next(specific_result.get_points())

        try:
            resource_id = uuid.UUID(resource_id)
            resource = get_resource(resource_id)
        except Exception as e:
            log.exception(e)
            continue
        if resource:
            log.debug(f'Found resource {resource.id}: {specific_values}')
            resource.metrics['views'] = specific_values['sum_nb_visits']
            try:
                resource.save(signal_kwargs={'ignores': ['post_save']})
            except Exception as e:
                log.exception(e)
                continue
        else:
            log.error('Resource not found', extra={
                'id': resource_id
            })


def update_community_resources_metrics_from_backend():
    '''
    Update community resource's metrics from backend.
    Get a sum of all metrics for `community_resource_views` on the backend and
    attach them to `community_resource.metrics`.
    '''
    log.info('Updating community resources metrics from backend...')
    client = metrics_client_factory()
    result = client.get_previous_day_measurements(collection='community_resource', tag='communityresource')
    process_metrics_result(client, result, CommunityResource)


def update_datasets_metrics_from_backend():
    '''
    Update datasets' metrics from backend.

    Get a sum of all metrics for `dataset_views` on the backend and
    attach them to `dataset.metrics`.
    '''
    log.info('Updating datasets metrics from backend...')
    client = metrics_client_factory()
    result = client.get_previous_day_measurements(collection='dataset', tag='dataset')
    process_metrics_result(client, result, Dataset)


def update_reuses_metrics_from_backend():
    '''
    Update reuses' metrics from backend.

    Get a sum of all metrics for `reuse_views` on the backend and
    attach them to `reuse.metrics`.
    '''
    log.info('Updating reuses metrics from backend...')
    client = metrics_client_factory()
    result = client.get_previous_day_measurements(collection='reuse', tag='reuse')
    process_metrics_result(client, result, Reuse)


def update_organizations_metrics_from_backend():
    '''
    Update organizations' metrics from backend.

    Get a sum of all metrics for `organization_views` on the backend and
    attach them to `organization.metrics`.
    '''
    log.info('Updating organizations metrics from backend...')
    client = metrics_client_factory()
    result = client.get_previous_day_measurements(collection='organization', tag='organization')
    process_metrics_result(client, result, Organization)


def update_users_metrics_from_backend():
    '''
    Update users' metrics from backend.

    Get a sum of all metrics for `user_views` on the backend and
    attach them to `user.metrics`.
    '''
    log.info('Updating users metrics from backend...')
    client = metrics_client_factory()
    result = client.get_previous_day_measurements(collection='user', tag='user_view')
    process_metrics_result(client, result, User)
