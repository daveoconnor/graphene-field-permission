import logging

logger = logging.getLogger(__name__)


class has_field_access():
    def __init__(self, *req_perms):
        self.req_perms = list(req_perms)

    def _permissions_filter(self, user_permissions, filter_id):
        try:
            filtered_perms = user_permissions[filter_id]
        except KeyError:
            error_msg = "You don't have any permissions on filter {}"
            raise ValueError(error_msg.format(filter_id))

        return filtered_perms

    def _has_access(self, user_permissions, filter_id=None):
        if filter_id is None:
            relevant_perms = user_permissions
        else:
            relevant_perms = self._permissions_filter(
                user_permissions,
                filter_id
            )

        logger.debug("check {} against req {}".format(
            relevant_perms,
            self.req_perms
        ))
        for perm in self.req_perms:
            logger.debug("check user has {} in {}".format(
                perm,
                relevant_perms,
            ))
            match = perm.lower() in relevant_perms

        return match

    def __call__(self, func, *args, **kwargs):
        def check(data, info, *args, **kwargs):
            logger.debug("check {} args: {} kwargs {}".format(
                func,
                args,
                kwargs
            ))
            permissions = info.context.user_permissions

            if not self._has_access(permissions, filter_id=str(data.id)):
                field = '_'.join(func.__name__.split('_')[1:])
                error_msg = "No access for user on field '{}'"
                raise Exception(error_msg.format(field))

            return func(data, info=info, *args, **kwargs)
        return check
