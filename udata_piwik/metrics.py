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


def process_metrics_result(result, model):
    model_str = model.__name__.lower()
    for (_, keys), _values in result.items():
        values = next(_values)
        values.pop('time')
        model_id = keys[model_str]

        model_result = model.objects.filter(id=model_id).first()

        if model_result:
            log.debug(f'Found {model_str} {model_result.id}: {values}')
            model_result.metrics['views'] = values['sum_nb_visits']
            try:
                model_result.save(signal_kwargs={'ignores': ['post_save']})
            except Exception as e:
                log.exception(e)
                continue
        else:
            log.error(f'{model_str} not found - id {model_id}')


def update_resources_metrics_from_backend():
    '''
    Update resource's metrics from backend.
    Get a sum of all metrics for `resource_views` on the backend and
    attach them to `resource.metrics`.
    '''
    log.info('Updating resources metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_resources()
    for (_, keys), _values in result.items():
        values = next(_values)
        values.pop('time')
        resource_id = keys['resource']
        try:
            resource_id = uuid.UUID(resource_id)
            resource = get_resource(resource_id)
        except Exception as e:
            log.exception(e)
            continue
        if resource:
            log.debug('Found resource %s: %s', resource.id, values)
            resource.metrics['views'] = values['sum_nb_visits']
            try:
                resource.save(signal_kwargs={'ignores': ['post_save']})
            except Exception as e:
                log.exception(e)
                continue
        else:
            log.error('Resource not found - id %s', resource_id)


def update_community_resources_metrics_from_backend():
    '''
    Update community resource's metrics from backend.
    Get a sum of all metrics for `community_resource_views` on the backend and
    attach them to `community_resource.metrics`.
    '''
    log.info('Updating community resources metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_community_resources()
    process_metrics_result(result, CommunityResource)


def update_datasets_metrics_from_backend():
    '''
    Update datasets' metrics from backend.

    Get a sum of all metrics for `dataset_views` on the backend and
    attach them to `dataset.metrics`.
    '''
    log.info('Updating datasets metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_datasets()
    process_metrics_result(result, Dataset)


def update_reuses_metrics_from_backend():
    '''
    Update reuses' metrics from backend.

    Get a sum of all metrics for `reuse_views` on the backend and
    attach them to `reuse.metrics`.
    '''
    log.info('Updating reuses metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_reuses()
    process_metrics_result(result, Reuse)


def update_organizations_metrics_from_backend():
    '''
    Update organizations' metrics from backend.

    Get a sum of all metrics for `organization_views` on the backend and
    attach them to `organization.metrics`.
    '''
    log.info('Updating organizations metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_organizations()
    process_metrics_result(result, Organization)


def update_users_metrics_from_backend():
    '''
    Update users' metrics from backend.

    Get a sum of all metrics for `user_views` on the backend and
    attach them to `user.metrics`.
    '''
    log.info('Updating users metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_users()
    for (_, keys), _values in result.items():
        values = next(_values)
        values.pop('time')
        user_id = keys['user_view']

        user = User.objects.filter(id=user_id).first()

        if user:
            log.debug(f'Found user {user.id}: {values}')
            user.metrics['views'] = values['sum_nb_visits']
            try:
                user.save(signal_kwargs={'ignores': ['post_save']})
            except Exception as e:
                log.exception(e)
                continue
        else:
            log.error(f'user not found - id {user_id}')
