import logging
import uuid

from datetime import date, time, datetime

from flask import current_app

from udata_metrics import metrics_client_factory

from udata.core.dataset.models import Dataset, get_resource
from udata.models import Reuse, User, Organization

KEYS = 'nb_uniq_visitors nb_hits nb_visits'.split()


log = logging.getLogger(__name__)


def update_metrics_from_backend():
    '''
    TODO: factorize those fns (maybe class based?)
    '''
    update_resources_metrics_from_backend()
    update_datasets_metrics_from_backend()
    update_reuses_metrics_from_backend()
    update_organizations_metrics_from_backend()
    update_users_metrics_from_backend()


def update_metrics_from_backend(result, model, model_str):
    for (_, keys), _values in result.items():
        values = next(_values)
        values.pop('time')
        model_id = keys[model_str]
        model_result = model.objects.filter(id=model_id).first()
        if model_result:
            log.debug(f'Found {model_str} {model_result.id}: {values}')
            model_result.metrics.update(values)
            try:
                # TODO: disable signals
                model_result.save()
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
    result = client.get_views_from_all_datasets()
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
            resource.metrics.update(values)
            try:
                # TODO: disable signals
                resource.save()
            except Exception as e:
                log.exception(e)
                continue
        else:
            log.error('Resource not found - id %s', resource_id)


def update_datasets_metrics_from_backend():
    '''
    Update datasets' metrics from backend.

    Get a sum of all metrics for `dataset_views` on the backend and
    attach them to `dataset.metrics`.
    '''
    log.info('Updating datasets metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_datasets()
    update_metrics_from_backend(Dataset, 'dataset', result)


def update_reuses_metrics_from_backend():
    '''
    Update reuses' metrics from backend.

    Get a sum of all metrics for `reuse_views` on the backend and
    attach them to `reuse.metrics`.
    '''
    log.info('Updating reuses metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_reuses()
    update_metrics_from_backend(Reuse, 'reuse', result)


def update_organizations_metrics_from_backend():
    '''
    Update organizations' metrics from backend.

    Get a sum of all metrics for `organization_views` on the backend and
    attach them to `organization.metrics`.
    '''
    log.info('Updating organizations metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_organizations()
    update_metrics_from_backend(Organization, 'organization', result)


def update_users_metrics_from_backend():
    '''
    Update users' metrics from backend.

    Get a sum of all metrics for `user_views` on the backend and
    attach them to `user.metrics`.
    '''
    log.info('Updating users metrics from backend...')
    client = metrics_client_factory()
    result = client.get_views_from_all_users()
    update_metrics_from_backend(User, 'user', result)
