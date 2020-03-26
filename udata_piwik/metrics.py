import logging
import uuid

from datetime import date, time, datetime

from flask import current_app, _app_ctx_stack

from udata.core.dataset.models import Dataset, get_resource

KEYS = 'nb_uniq_visitors nb_hits nb_visits'.split()


log = logging.getLogger(__name__)


def get_backend_client():
    ctx = _app_ctx_stack.top
    if ctx is not None and hasattr(ctx, 'influx_db'):
        return ctx.influx_db


def update_metrics_from_backend():
    '''
    TODO: factorize those fns (maybe class based?)
    '''
    update_resources_metrics_from_backend()
    update_datasets_metrics_from_backend()


def update_resources_metrics_from_backend():
    '''
    Update resources' metrics from backend.

    Get a sum of all metrics for `resource_views` on the backend and
    attach them to `resource.metrics`.
    '''
    log.info('Updating resources metrics from backend...')
    client = get_backend_client()
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
    client = get_backend_client()
    result = client.get_views_from_all_datasets()
    for (_, keys), _values in result.items():
        values = next(_values)
        values.pop('time')
        dataset_id = keys['dataset']
        dataset = Dataset.objects.filter(id=dataset_id).first()
        if dataset:
            log.debug('Found dataset %s: %s', dataset.id, values)
            dataset.metrics.update(values)
            try:
                # TODO: disable signals
                dataset.save()
            except Exception as e:
                log.exception(e)
                continue
        else:
            log.error('Dataset not found - id %s', dataset_id)


def upsert_metric_for_resource(resource, dataset, day, data):
    if not dataset:
        log.error('No dataset linked to resource %s', resource.id)
        return
    author_type, author = ('organization', dataset.organization) \
        if dataset.organization else ('user', dataset.owner)
    upsert_in_metrics_backend(
        day=day,
        metric='resource_views',
        tags={
            'author_type': author_type if author else None,
            'author': author.id if author else None,
            'dataset': dataset.id,
            'resource': resource.id,
        },
        data=data,
    )


def upsert_metric_for_dataset(dataset, day, data):
    author_type, author = ('organization', dataset.organization) \
        if dataset.organization else ('user', dataset.owner)
    upsert_in_metrics_backend(
        day=day,
        metric='dataset_views',
        tags={
            'author_type': author_type if author else None,
            'author': author.id if author else None,
            'dataset': dataset.id,
        },
        data=data,
    )


def upsert_metric_for_reuse(reuse, day, data):
    author_type, author = ('organization', reuse.organization) \
        if reuse.organization else ('user', reuse.owner)
    upsert_in_metrics_backend(
        day=day,
        metric='reuse_views',
        tags={
            'author_type': author_type if author else None,
            'author': author.id if author else None,
            'reuse': reuse.id,
        },
        data=data,
    )


def upsert_metric_for_organization(org, day, data):
    upsert_in_metrics_backend(
        day=day,
        metric='organization_views',
        tags={
            'organization': org.id,
        },
        data=data,
    )


def upsert_metric_for_user(user, day, data):
    upsert_in_metrics_backend(
        day=day,
        metric='user_views',
        tags={
            'user': user.id,
        },
        data=data,
    )


def upsert_in_metrics_backend(day=None, metric=None, tags={}, data={}):
    if isinstance(day, str):
        day = date.fromisoformat(day)
    # we're on a daily basis, but backend is not
    dt = datetime.combine(day or date.today(), time())
    client = get_backend_client()
    body = {
        'time': dt,
        'measurement': metric,
        'tags': tags,
        'fields': dict((k, data[k]) for k in KEYS)
    }
    client.insert(body)
