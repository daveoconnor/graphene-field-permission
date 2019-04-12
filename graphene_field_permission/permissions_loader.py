import importlib
import logging
logger = logging.getLogger(__name__)


def import_django_settings():
    from django.conf import settings
    config = settings.GRAPHENE_FIELD_PERMISSION
    return config['SRC_MODULE'], config['SRC_METHOD']


def import_settings():
    try:
        return import_django_settings()
    except ImportError as exc:
        logger.debug("django.conf not imported.")

    # TODO: other frameworks here

    raise ImportError('No configured settings found.')


def get_permissions_method():
    try:
        src_mod, src_method = import_settings()
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

    return getattr(permissions_helper, src_method, None)
