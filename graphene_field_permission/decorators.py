import logging

logger = logging.getLogger(__name__)


class has_field_access():
    def __init__(self, *req_perms, filter_field=None):
        self.filter_field = filter_field
        self.req_perms = list(req_perms)

    def _permissions_filter(self, user_permissions, filter_id):
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

    def _get_filter_data(self, data, filter_field):
        logger.debug("_get_filter_data data: {}, filter_field: {}".format(
            data,
            filter_field
        ))
        filter_list = filter_field.split('.')
        # traverse the related data
        while len(filter_list):
            related = filter_list.pop(0)
            if not hasattr(data, related):
                error_msg = "{} not found on {}. Modify the filter_field."
                raise Exception(error_msg.format(related, type(data), data))
            data = getattr(data, related)

        logger.debug("_get_filter_data return data {}".format(data))
        return str(data)

    def _has_access(self, user_permissions, filter_id=None):
        if filter_id is None:
            relevant_perms = user_permissions
        else:
            relevant_perms = self._permissions_filter(
                user_permissions,
                filter_id
            )

        for perm in self.req_perms:
            logger.debug("check user has {} in {}".format(
                perm,
                relevant_perms,
            ))
            try:
                match = relevant_perms[perm.lower()]
                return match
            except KeyError:
                pass

        raise KeyError('no match found on {} against {}'.format(
            self.req_perms,
            relevant_perms,
        ))

    def __call__(self, func, *args, **kwargs):
        def check(data, info, *args, **kwargs):
            logger.debug("check {} args: {} kwargs {}".format(
                func,
                args,
                kwargs
            ))
            permissions = info.context.user_permissions

            filter_id = None
            if self.filter_field is not None:
                filter_id = self._get_filter_data(data, self.filter_field)

            try:
                self._has_access(permissions, filter_id=filter_id)
            except KeyError:
                field = '_'.join(func.__name__.split('_')[1:])
                error_msg = "No access for user on field '{}'"
                raise Exception(error_msg.format(field))

            return func(data, info=info, *args, **kwargs)
        return check
