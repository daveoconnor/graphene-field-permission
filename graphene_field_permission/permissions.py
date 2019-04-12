import logging
from . import api

logger = logging.getLogger(__name__)


class PermissionsMiddleware():
    def on_error(self, error):
        logger.error(error)

    def resolve(self, next, root, info, **kwargs):
        # have to check 'id' because AnonymousUser is
        # considered authed for some reason
        if info.context.user.id:
            if not hasattr(self, 'permissions'):
                self.permissions = api.fetch_permissions(
                    info.context.user
                )
            info.context.user_permissions = self.permissions

        return next(root, info, **kwargs)
