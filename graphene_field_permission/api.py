import logging
from . import permissions_loader

logger = logging.getLogger(__name__)


def permissions_filter(user_permissions, filter_id):
    logger.debug("_permissions_filter: find {} in {}".format(
        filter_id,
        user_permissions
    ))
    try:
        filtered_perms = user_permissions[filter_id]
    except KeyError:
        error_msg = "You don't have any permissions on filter {}"
        raise ValueError(error_msg.format(filter_id))

    return filtered_perms


def get_filter_data(data, filter_field):
    filter_list = filter_field.split('.')
    # traverse the related data
    while len(filter_list):
        related = filter_list.pop(0)
        if not hasattr(data, related):
            error_msg = "{} not found on {}. Modify the filter_field."
            raise Exception(error_msg.format(related, type(data), data))
        data = getattr(data, related)

    return str(data)


def _has_access(*required_permissions, user_permissions, filter_id=None):
    if filter_id is None:
        relevant_permissions = user_permissions
    else:
        relevant_permissions = permissions_filter(
            user_permissions,
            filter_id
        )

    for perm in required_permissions:
        logger.debug("check user has {} in {}".format(
            perm,
            relevant_permissions,
        ))
        try:
            match = relevant_permissions[perm.lower()]
            return match
        except KeyError:
            pass

    raise PermissionError('no match found on {} against {}'.format(
        required_permissions,
        relevant_permissions,
    ))


def restructure_permissions(raw_permissions):
    if isinstance(raw_permissions, list):
        return {value: True for value in raw_permissions}
    elif isinstance(raw_permissions, dict):
        permissions = {}
        for group in raw_permissions:
            group_perms = {value: True for value in raw_permissions[group]}
            permissions[group] = group_perms
        return permissions


def fetch_permissions(user):
    permissions_func = permissions_loader.get_permissions_method()
    permissions_list = permissions_func(user)
    permissions = restructure_permissions(permissions_list)
    logger.debug("fetch_permissions: {}".format(permissions))
    return permissions


def check_field_access(*required_permissions, filter_field=None, filter_data=None, info_context):
    """
    Confirms user has access to a permission
    :param required_permissions: multiple arguments, one of which is required
    to be listed in user_permissions
    :param filter_field: field/hierarchy to look up, dot separated
    :param filter_data: traversed for value if filter_field is set
    :param info_context the info.context object from graphene
    :raises PermissionException if no permissions assigned
    """
    filter_id = None
    if filter_field is not None:
        if filter_data is None:
            raise AttributeError('filter_data has no data. Must be set when filter_field is set')
        filter_id = get_filter_data(filter_data, filter_field)

    user_permissions = fetch_permissions(
        info_context.user
    )

    return _has_access(
        *required_permissions,
        user_permissions=user_permissions,
        filter_id=filter_id
    )