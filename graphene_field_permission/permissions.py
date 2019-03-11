import importlib
import logging
logger = logging.getLogger(__name__)


class PermissionsMiddleware():
    def on_error(self, error):
        logger.error(error)

    def __import_django_settings(self):
        from django.conf import settings
        config = settings.GRAPHENE_FIELD_PERMISSION
        return config['SRC_MODULE'], config['SRC_METHOD']

    def __import_settings(self):
        try:
            return self.__import_django_settings()
        except ImportError as exc:
            logger.debug("django.conf not imported.")

        # TODO: other frameworks here

        raise ImportError('No configured settings found.')

    def __fetch_permissions(self, user):
        self.permissions = {}
        try:
            src_mod, src_method = self.__import_settings()
        except ImportError as exc1:
            error_msg = 'Failed to import any settings. Check your config.'
            raise Exception(error_msg) from exc1
        except AttributeError as exc2:
            error_msg = 'missing GRAPHENE_FIELD_PERMISSION in django.conf.'
            raise Exception(error_msg) from exc2
        except KeyError as exc3:
            error_msg = 'missing GRAPHENE_FIELD_PERMISSION values.'
            raise Exception(error_msg) from exc3

        try:
            permissions_helper = importlib.import_module(src_mod)
        except Exception as exc:
            error_msg = "UserPermissions module not found at {}"
            raise Exception(error_msg.format(src_mod)) from exc

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
