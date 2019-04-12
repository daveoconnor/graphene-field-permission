import logging
from . import api

logger = logging.getLogger(__name__)


class has_field_access():
    def __init__(self, *req_perms, filter_field=None):
        self.filter_field = filter_field
        self.req_perms = req_perms

    def __call__(self, func, *args, **kwargs):
        def check(data, info, *args, **kwargs):
            try:
                api.check_field_access(
                    *self.req_perms,
                    info_context=info.context,
                    filter_field=self.filter_field,
                    filter_data=data
                )
            except PermissionError:
                field = '_'.join(func.__name__.split('_')[1:])
                error_msg = "No access for user on field '{}'"
                raise Exception(error_msg.format(field))

            return func(data, info=info, *args, **kwargs)
        return check
