from django.conf import settings
import importlib
import logging
logger = logging.getLogger(__name__)


class PermissionsMiddleware():
    def on_error(self, error):
        logger.error(error)

    def __fetch_permissions(self, user):
        self.permissions = {}

        src_mod = settings.GRAPHENE_FIELD_PERMISSION.get('SRC_MODULE', None)
        src_method = settings.GRAPHENE_FIELD_PERMISSION.get('SRC_METHOD', None)
        if src_mod is None:
            error_msg = 'settings.GRAPHENE_FIELD_PERMISSION.SRC_MODULE not set'
            raise Exception(error_msg)
        if src_method is None:
            error_msg = 'settings.GRAPHENE_FIELD_PERMISSION.SRC_METHOD not set'
            raise Exception(error_msg)

        try:
            permissions_helper = importlib.import_module(src_mod)
        except Exception:
            error_msg = "UserPermissions module not found at {}"
            raise Exception(error_msg.format(src_mod))

        func = getattr(permissions_helper, src_method, None)
        logger.debug("permissions function {}".format(func))
        if func is None:
            logger.error("SRC_METHOD {} not found on {}".format(
                src_method,
                src_mod
            ))
        permissions = func(user)
        logger.debug("permissions: {}".format(permissions))
        self.permissions = permissions

    def resolve(self, next, root, info, **kwargs):
        # have to check 'id' because AnonymousUser is
        # considered authed for some reason
        if info.context.user.id:
            if not hasattr(self, 'permissions'):
                self.__fetch_permissions(info.context.user)
            else:
                info.context.user_permissions = self.permissions

        return next(root, info, **kwargs)
